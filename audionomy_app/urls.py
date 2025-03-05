from django.urls import path
from .views import (
    home,
    manage_dataset,
    add_entry,
    delete_entry,
    export_dataset,            # CSV export (existing)
    export_dataset_json,       # New: JSON export
    export_dataset_parquet,    # New: Parquet export
    export_audio_zip,          # New: ZIP export of audio files
    edit_entry
)

urlpatterns = [
    path("", home, name="home"),
    path("manage/<int:dataset_id>/", manage_dataset, name="manage_dataset"),
    path("add_entry/<int:dataset_id>/", add_entry, name="add_entry"),
    path("delete_entry/<int:entry_id>/", delete_entry, name="delete_entry"),
    path("export/csv/<int:dataset_id>/", export_dataset, name="export_dataset_csv"),
    path("export/json/<int:dataset_id>/", export_dataset_json, name="export_dataset_json"),
    path("export/parquet/<int:dataset_id>/", export_dataset_parquet, name="export_dataset_parquet"),
    path("export/zip/<int:dataset_id>/", export_audio_zip, name="export_audio_zip"),
    path("edit_entry/<int:entry_id>/", edit_entry, name="edit_entry"),
]
