from django.db import models

# Create your models here.
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class TranslationFr2EnModel:
    def __init__(self):
        # Load the tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained("/root/server/MyPersonalWebServer/webserver/translator/models/fr_to_en")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("/root/server/MyPersonalWebServer/webserver/translator/models/fr_to_en")
    
    def translate(self, text):
        # Tokenize the input text
        inputs = self.tokenizer(text, return_tensors="pt")
        
        # Generate translation
        outputs = self.model.generate(**inputs, max_length=100, num_beams=3)
        
        # Decode the output and return the translated text
        translated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translated_text
    
class TranslationEn2FrModel:
    def __init__(self):
        # Load the tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained("/root/server/MyPersonalWebServer/webserver/translator/models/en_to_fr")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("/root/server/MyPersonalWebServer/webserver/translator/models/en_to_fr")
    
    def translate(self, text):
        # Tokenize the input text
        inputs = self.tokenizer(text, return_tensors="pt")
        
        # Generate translation
        outputs = self.model.generate(**inputs, max_length=100, num_beams=3)
        
        # Decode the output and return the translated text
        translated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translated_text