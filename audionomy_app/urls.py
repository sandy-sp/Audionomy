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
from . import views

urlpatterns = [
    # Home page: shows list of datasets & form to create new one
    path('', views.home, name='home'),

    # Manage a specific dataset: list entries, links to add or export
    path('manage/<int:dataset_id>/', views.manage_dataset, name='manage_dataset'),

    # Add a new audio entry to a given dataset
    path('manage/<int:dataset_id>/add_entry/', views.add_entry, name='add_entry'),

    # Export dataset (placeholder in views)
    path('manage/<int:dataset_id>/export/', views.export_dataset, name='export_dataset'),
]
