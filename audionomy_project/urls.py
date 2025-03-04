"""
URL configuration for audionomy_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('audionomy_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
URL configuration for the Audionomy Project.

This file defines the top-level URL routing for the Django project named
'audionomy_project'. It includes:

- Admin site routes (for Django's admin panel).
- Application routes from 'audionomy_app.urls'.
- Automatic serving of media files during development (if DEBUG=True).

Reference:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
    https://docs.djangoproject.com/en/4.2/howto/static-files/#serving-files-uploaded-by-a-user
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin route:
    path('admin/', admin.site.urls),
    # Include our custom app's URLs:
    path('', include('audionomy_app.urls')),
]

if settings.DEBUG:
    """
    In development mode, serve user-uploaded media files from MEDIA_URL
    using Django’s built-in static file server.

    WARNING:
        In production, do NOT use this for serving media; configure a proper
        media file host or a cloud service. 
    """
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
