from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('manage/<int:dataset_id>/', views.manage_dataset, name='manage_dataset'),
    path('manage/<int:dataset_id>/add_entry/', views.add_entry, name='add_entry'),
    path('manage/<int:dataset_id>/export/', views.export_dataset, name='export_dataset'),
]
