from django.shortcuts import render
from django.apps import apps
from django.http import JsonResponse
from django.conf import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def rag_query_view(request):
    print(settings.OPENAI_API_KEY)
    query = request.GET.get("q", "")
    if not query:
        return JsonResponse({"error": "Missing query"}, status=400)

    # Step 1: Retrieve documents
    rag_service = apps.get_app_config("stevenai").rag_service
    retrieved_docs = rag_service.search(query)

    # Step 2: Format context
    context_chunks = []
    for entry in retrieved_docs.get("qa", []) + retrieved_docs.get("docs", []):
        if isinstance(entry, dict):
            context_chunks.append(entry.get("answer") or entry.get("doc") or "")
        else:
            context_chunks.append(str(entry))
    context = "\n\n".join(context_chunks)

    full_prompt = (
        f'Someone asked you: "{query}"\n\n'
        f"To help you answer, we've retrieved some relevant information from your background:\n\n"
        f"{context}\n\n"
        f"Now, reply as if you're chatting with them directly. Keep it casual."
        f"If the information above does not help answer the question, simply say you don't know."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Steven (Hongyuan Liu), an AI version of yourself built to talk conversationally "
                        "and help people understand your work, background, and projects. Always be friendly and honest."
                    ),
                },
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
