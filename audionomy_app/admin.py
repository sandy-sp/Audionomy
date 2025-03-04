"""
Django Admin configuration for the audionomy_app.

This file defines how the Dataset and AudioEntry models appear and behave
in the Django admin site, letting administrators view, search, and manage records.

Reference:
    https://docs.djangoproject.com/en/4.2/ref/contrib/admin/
"""

from django.contrib import admin
from .models import Dataset, AudioEntry


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    """
    Customize how Dataset objects are displayed in the admin.
    - Shows 'name' and 'created_at' in the list view.
    - Allows searching by 'name'.
    - Provides a date hierarchy based on 'created_at' if desired.
    """
    list_display = ("name", "created_at")
    search_fields = ("name",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(AudioEntry)
class AudioEntryAdmin(admin.ModelAdmin):
    """
    Customize how AudioEntry objects are displayed in the admin.
    - Lists title, dataset, durations, and creation date.
    - Enables searching by 'title'.
    - Allows filtering by 'dataset'.
    """
    list_display = (
        "title",
        "dataset",
        "audio1_duration",
        "audio2_duration",
        "created_at"
    )
    search_fields = ("title",)
    list_filter = ("dataset",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
