"""
URL configuration for the audionomy_app.

This file defines the routes for our Django app and maps them to view functions
in views.py. It includes:

- Home route ('') -> home() view
- Manage dataset route ('manage/<int:dataset_id>/') -> manage_dataset() view
- Add entry route ('manage/<int:dataset_id>/add_entry/') -> add_entry() view
- Export dataset route ('manage/<int:dataset_id>/export/') -> export_dataset() view

See also:
audionomy_project/urls.py -> includes these routes at the root level.
"""

from django.urls import path
from .views import (
    home, manage_dataset, add_entry, delete_entry, export_dataset, edit_entry
)

urlpatterns = [
    path("", home, name="home"),
    path("manage/<int:dataset_id>/", manage_dataset, name="manage_dataset"),
    path("add_entry/<int:dataset_id>/", add_entry, name="add_entry"),
    path("delete_entry/<int:entry_id>/", delete_entry, name="delete_entry"),
    path("export_dataset/<int:dataset_id>/", export_dataset, name="export_dataset"),
    path("edit_entry/<int:entry_id>/", edit_entry, name="edit_entry"),  # ✅ Fix
]
