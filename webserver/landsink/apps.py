from django.apps import AppConfig
from . import models


class LandsinkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'landsink'    
    models.build_models()
