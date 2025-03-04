"""
Django settings for audionomy_project.

This file defines all the core configuration for the Audionomy Django project,
including:
  - Installed apps
  - Middleware
  - Templates configuration
  - Database
  - Static & media file settings
  - Security & debug toggles

Usage:
  - Typically, you don't run this file directly.
  - It's referenced when you run manage.py or any Django command with
    DJANGO_SETTINGS_MODULE="audionomy_project.settings".

Environment Variables:
  - AUDIONOMY_SECRET_KEY: (Optional) Secret key for production usage.
  - AUDIONOMY_DEBUG: "True"/"False" to toggle DEBUG mode.
  - OTHER DB or specialized variables if you want more advanced environment-based config.

For more info, see:
https://docs.djangoproject.com/en/4.2/topics/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file if present (optional)
# Make sure you have python-dotenv installed if you want to use this approach.
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------------------
# SECURITY / SECRET KEY
# ------------------------------------------------------------------------------
# SECURITY WARNING: keep the secret key used in production secret!
# We'll attempt to read from AUDIONOMY_SECRET_KEY environment variable.
# If not found and in debug mode, use a default dev key (NOT for production).
SECRET_KEY = os.environ.get("AUDIONOMY_SECRET_KEY", "dev-insecure-secret-key")


# ------------------------------------------------------------------------------
# DEBUG MODE
# ------------------------------------------------------------------------------
# WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("AUDIONOMY_DEBUG", "True") == "True"

ALLOWED_HOSTS = []
# In production, you'll set ALLOWED_HOSTS to your domain or server IPs.


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
        # If you want to store templates in a custom folder, you can define:
        # 'DIRS': [BASE_DIR / "templates"],
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Default Django processors:
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'audionomy_project.wsgi.application'
# If using ASGI, you can also set ASGI_APPLICATION here.


# ------------------------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------------------------
# Defaults to SQLite for development. For Postgres or MySQL,
# read from environment or adjust here accordingly.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ------------------------------------------------------------------------------
# PASSWORD VALIDATION
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ------------------------------------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# ------------------------------------------------------------------------------
# STATIC FILES
# https://docs.djangoproject.com/en/4.2/howto/static-files/
# ------------------------------------------------------------------------------
STATIC_URL = '/static/'
# For production, set STATIC_ROOT = BASE_DIR / 'static_collected' or similar
# Then run 'python manage.py collectstatic' to gather static files.


# ------------------------------------------------------------------------------
# MEDIA FILES (User uploads, e.g. audio files)
# https://docs.djangoproject.com/en/4.2/topics/files/
# ------------------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# This is where your FileField/ImageField data gets saved.
# In dev, runserver can serve media if DEBUG=True and you set up urls for it.


# ------------------------------------------------------------------------------
# DEFAULT PRIMARY KEY FIELD TYPE
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ------------------------------------------------------------------------------
# CUSTOM / PROJECT-SPECIFIC SETTINGS
# ------------------------------------------------------------------------------
# If you want to define custom logic or read more environment variables,
# you can do it at the bottom here. For example:
#
# AUDIO_PROCESSING_ENABLED = (os.environ.get("AUDIO_PROCESSING", "True") == "True")
# ...
#
# End of file: settings.py
