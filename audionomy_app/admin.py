from django.contrib import admin
from .models import Dataset, AudioEntry

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(AudioEntry)
class AudioEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'dataset')
