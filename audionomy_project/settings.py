"""
Django settings for audionomy_project.

This file defines the core configuration for the Audionomy Django project,
including installed apps, middleware, templates, database settings, and static/media configurations.

Environment variables (optionally loaded via a .env file) are used for sensitive or
environment-specific settings such as SECRET_KEY, DEBUG, and the database configuration.

For more details, see:
https://docs.djangoproject.com/en/4.2/topics/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------------------
# SECURITY / SECRET KEY
# ------------------------------------------------------------------------------
# Keep the secret key used in production secret!
SECRET_KEY = os.environ.get("AUDIONOMY_SECRET_KEY", "dev-insecure-secret-key")

# ------------------------------------------------------------------------------
# DEBUG MODE
# ------------------------------------------------------------------------------
DEBUG = os.environ.get("AUDIONOMY_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",") if not DEBUG else []

# ------------------------------------------------------------------------------
# APPLICATIONS
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'audionomy_app',  # Our custom Django app
]

# ------------------------------------------------------------------------------
# MIDDLEWARE
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ------------------------------------------------------------------------------
# URL CONFIGURATION
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'audionomy_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # To use custom template directories, add them here (e.g., BASE_DIR / "templates")
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Default Django context processors:
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'audionomy_project.wsgi.application'
# For ASGI deployments, set ASGI_APPLICATION here if needed.

# ------------------------------------------------------------------------------
# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# Use MySQL for scalability. Ensure you have mysqlclient installed.
# You can override these defaults using environment variables.
DATABASES = {
    'default': {
        'ENGINE': os.environ.get("DB_ENGINE", "django.db.backends.mysql"),
        'NAME': os.environ.get("DB_NAME", "audionomy"),
        'USER': os.environ.get("DB_USER", "root"),
        'PASSWORD': os.environ.get("DB_PASSWORD", ""),
        'HOST': os.environ.get("DB_HOST", "localhost"),
        'PORT': os.environ.get("DB_PORT", "3306"),
    }
}
# For local development with SQLite, you can temporarily switch the ENGINE:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# ------------------------------------------------------------------------------
# PASSWORD VALIDATION
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ------------------------------------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.environ.get("TIME_ZONE", "UTC")
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# STATIC FILES
# ------------------------------------------------------------------------------
STATIC_URL = '/static/'
# For production, set STATIC_ROOT (e.g., STATIC_ROOT = BASE_DIR / 'static_collected')
# and run 'python manage.py collectstatic' to collect static files.

# ------------------------------------------------------------------------------
# MEDIA FILES (User uploads)
# ------------------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Uploaded files via FileField/ImageField will be stored here.

# ------------------------------------------------------------------------------
# DEFAULT PRIMARY KEY FIELD TYPE
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------------------------------------------------------
# CUSTOM / PROJECT-SPECIFIC SETTINGS
# ------------------------------------------------------------------------------
# Example: AUDIO_PROCESSING_ENABLED = os.environ.get("AUDIO_PROCESSING", "True") == "True"
# Additional settings can be added below as needed.
