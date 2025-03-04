from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('manage/<int:dataset_id>/', views.manage_dataset, name='manage_dataset'),
    # etc.
]
