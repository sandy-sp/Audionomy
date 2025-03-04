"""
Django App Configuration for audionomy_app.

This file defines the AudionomyAppConfig class, which tells Django about
our app's name and optional startup hooks. By default, it's enough to set
the 'name' and any auto field settings. If you need signals or custom
initialization code on app load, you can override ready().
"""

from django.apps import AppConfig


class AudionomyAppConfig(AppConfig):
    """
    Django application configuration for 'audionomy_app'.

    Attributes:
        default_auto_field: Specifies the type of auto-increment primary key.
        name: The Python path to this application, used by Django's registry.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audionomy_app'

    def ready(self):
        """
        This method is called by Django once the application registry is fully populated.
        You can import signals or run initialization logic here if needed.

        Example (Uncomment if you have signals):
            from . import signals
        """
        pass
