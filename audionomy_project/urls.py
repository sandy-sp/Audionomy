"""
URL configuration for the Audionomy project.

This file routes URLs to views. It includes:
  - The Django admin site.
  - The URL patterns defined in the audionomy_app application.
  - Automatic serving of media files during development.
  
For more details, see:
https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin route
    path('admin/', admin.site.urls),
    # Include URL patterns from audionomy_app
    path('', include('audionomy_app.urls')),
]

if settings.DEBUG:
    # Serve media files from MEDIA_URL during development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
