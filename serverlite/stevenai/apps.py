from django.apps import AppConfig
from . import models


class StevenaiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stevenai"
    rag_service = models.RAGSearchService()
    print("✅ RAGSearchService initialized and stored in apps.py")
