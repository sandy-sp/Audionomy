from django.apps import AppConfig

class AudionomyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audionomy_app'

    def ready(self):
        # This method is called once the app registry is fully populated.
        # Import any signals here to ensure they are registered.
        # Example:
        # from . import signals
        pass
