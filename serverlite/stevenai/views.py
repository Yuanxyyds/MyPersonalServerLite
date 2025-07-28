from django.shortcuts import render
from django.apps import apps
from django.http import JsonResponse
from django.conf import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_openai_response(query, include_qa=False, include_docs=False):
    if not query:
        return JsonResponse({"error": "Missing query"}, status=400)

    # Step 1: Retrieve documents
    rag_service = apps.get_app_config("stevenai").rag_service
    retrieved_docs = rag_service.search(
        query, include_qa=include_qa, include_docs=include_docs
    )

    # Step 2: Format context
    context_chunks = []
    for entry in retrieved_docs.get("qa", []) + retrieved_docs.get("docs", []):
        if isinstance(entry, dict):
            context_chunks.append(entry.get("answer") or entry.get("doc") or "")
        else:
            context_chunks.append(str(entry))
    context = "\n\n".join(context_chunks)

    system_prompt = (
        "You are Steven (Hongyuan Liu). "
        "You're here to help people understand your work, background, projects, and experiences. "
        "If a question isn’t about you, or the info retrieved doesn’t help, just say you can’t answer or that it’s outside your knowledge."
    )

    full_prompt = (
        f'Someone asked you: "{query}"\n\n'
        f"To help answer, we've retrieved the following relevant information from your background:\n\n"
        f"{context}\n\n"
        f"Based on this, please reply naturally as yourself."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt},
            ],
            temperature=0.5,
            max_tokens=512,
        )

        answer = response.choices[0].message.content
        return JsonResponse(
            {"query": query, "answer": answer, "context_used": context_chunks}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def openai_qa_only(request):
    query = request.GET.get("q", "")
    return generate_openai_response(query, include_qa=True, include_docs=False)


def openai_docs_only(request):
    query = request.GET.get("q", "")
    return generate_openai_response(query, include_qa=False, include_docs=True)


def openai_qa_docs(request):
    query = request.GET.get("q", "")
    return generate_openai_response(query, include_qa=True, include_docs=True)
