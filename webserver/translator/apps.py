from django.apps import AppConfig
from . import models


class Translator(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'translator'
    translation_fr2en_model = models.TranslationFr2EnModel()
    translation_en2fr_model = models.TranslationEn2FrModel()
