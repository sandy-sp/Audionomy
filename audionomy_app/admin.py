"""
Django Admin configuration for audionomy_app.

This file defines how the Dataset and AudioEntry models appear and behave
in the Django admin site, allowing administrators to view, search, filter, 
and manage audio datasets and entries.
"""

from django.contrib import admin
from .models import Dataset, AudioEntry


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    """
    Admin view configuration for Dataset.
    
    - Displays the dataset name and creation date.
    - Allows searching by name.
    - Provides date hierarchy for creation dates.
    """
    list_display = ("name", "created_at")
    search_fields = ("name",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(AudioEntry)
class AudioEntryAdmin(admin.ModelAdmin):
    """
    Admin view configuration for AudioEntry.
    
    - Displays key metadata: title, associated dataset, model used,
      audio durations, and creation date.
    - Allows searching by title and filtering by dataset.
    - Provides date hierarchy for creation dates.
    - Extra fields such as lyrics, persona, and sample file can be viewed 
      by clicking into the detail page.
    """
    list_display = (
        "title",
        "dataset",
        "model_used",
        "audio1_duration",
        "audio2_duration",
        "created_at"
    )
    search_fields = ("title", "style_prompt", "exclude_style_prompt", "model_used")
    list_filter = ("dataset",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
