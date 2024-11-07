from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . import apps
import json

@csrf_exempt
def translate_fr_to_en(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get("text", "")
            
            if not text:
                return JsonResponse({"error": "No text provided for translation"}, status=400)
            
            # Use the model to perform the translation
            translated_text = apps.Translator.translation_fr2en_model.translate(text)
            
            # Return the translated text
            return JsonResponse({
                "original_text": text,
                "translated_text": translated_text
            })
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
    
@csrf_exempt
def translate_en_to_fr(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get("text", "")
            
            if not text:
                return JsonResponse({"error": "No text provided for translation"}, status=400)
            
            # Use the model to perform the translation
            translated_text = apps.Translator.translation_en2fr_model.translate(text)
            
            # Return the translated text
            return JsonResponse({
                "original_text": text,
                "translated_text": translated_text
            })
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)