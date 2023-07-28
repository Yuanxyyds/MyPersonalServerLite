from django.apps import AppConfig


class LandSinkConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "landSink"

    def ready(self):
        # Import the necessary model and call the build_models() function here
        from landSink import model
        model.build_models()
