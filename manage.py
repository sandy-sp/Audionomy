#!/usr/bin/env python
"""
manage.py for the Audionomy Django Project.

This script is Django’s command-line utility for administrative tasks,
such as running the development server, applying database migrations,
creating a superuser, collecting static files, etc.

Usage:
    poetry run python manage.py runserver
    poetry run python manage.py migrate
    poetry run python manage.py createsuperuser
    ...

Environment:
    - By default, this sets DJANGO_SETTINGS_MODULE to 'audionomy_project.settings'.
    - If you need a different config, set DJANGO_SETTINGS_MODULE manually or
      create separate settings for staging / production.

Example:
    DJANGO_SETTINGS_MODULE="audionomy_project.settings_production" poetry run python manage.py runserver
"""

import os
import sys


def main():
    """
    Main entry point for Django’s administrative tasks.

    Steps:
    1. Set the default settings module to 'audionomy_project.settings' if not already set.
    2. Execute Django's built-in command-line utility with provided arguments.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "audionomy_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Could not import Django. Ensure it is installed and "
            "available on your PYTHONPATH environment variable. "
            "Did you forget to activate your virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
