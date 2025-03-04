"""
Models for the audionomy_app.

This module defines two primary models:
  1. Dataset: Groups a set of audio entries under one name.
  2. AudioEntry: Represents a specific audio item with optional file uploads and metadata.

Features:
  - Each AudioEntry can hold up to two audio files, automatically computing their durations via pydub.
  - The custom 'audio_upload_path' function organizes uploaded files under:
      media/audio/<dataset_name>/<sanitized_filename>
  - On creation or update, if new files are uploaded, the model recalculates durations for audio_file_1 and audio_file_2.
"""

import os
import re
from pathlib import Path

from django.db import models
from django.conf import settings
from django.core.files import File
from pydub import AudioSegment


class Dataset(models.Model):
    """
    Represents a named group of audio entries.

    Fields:
        name (str, unique): The dataset's name, e.g., 'Instrumentals 2025'.
        created_at (DateTime): Auto-set to creation time.

    Example:
        dataset = Dataset.objects.create(name="MyInstrumentalCollection")
        dataset.entries.all()  # retrieves related AudioEntry objects
    """
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


def audio_upload_path(instance, filename):
    """
    Custom file upload path for audio files.

    This function:
      1) Removes any characters outside [a-zA-Z0-9._-].
      2) Takes the dataset's name, replaces spaces with underscores.
      3) Returns a relative path: "audio/<dataset_name>/<safe_filename>"

    This path is appended to MEDIA_ROOT when saving the file.

    Args:
        instance (AudioEntry): The model instance being saved.
        filename (str): Original filename from the upload.

    Returns:
        str: A relative path under "audio/<dataset_name>" for the sanitized filename.
    """
    safe_filename = re.sub(r"[^a-zA-Z0-9._-]+", "", filename)
    dataset_name = instance.dataset.name.replace(" ", "_")
    return f"audio/{dataset_name}/{safe_filename}"


class AudioEntry(models.Model):
    """
    A single audio entry within a Dataset, storing metadata and up to two files.

    Fields:
        dataset (ForeignKey): Links to a Dataset, with CASCADE deletion.
        title (str): Title or name of the audio piece.
        style_prompt (str): Optional style/mood descriptor.
        exclude_style_prompt (str): Optional field describing what style to exclude.
        model_used (str): E.g., the AI model or generation method used, if relevant.
        youtube_link (URLField): Optional link to YouTube, if an external reference exists.
        created_at (DateTime): Auto-set creation datetime.
        audio_file_1, audio_file_2 (FileField): Up to two audio uploads.
        audio1_duration, audio2_duration (float): Auto-computed durations in seconds.

    Behavior:
      - On initial save (and subsequent if new files are uploaded):
        * The file(s) are saved.
        * We attempt to compute durations using pydub. If successful, fields are updated.
      - If the file is missing or unsupported format, the duration defaults to 0.0.

    Example:
        AudioEntry.objects.create(
            dataset=some_dataset,
            title="PianoTrack",
            audio_file_1=some_file,
        )
    """
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='entries'
    )

    # Basic metadata
    title = models.CharField(max_length=255)
    style_prompt = models.CharField(max_length=255, blank=True)
    exclude_style_prompt = models.CharField(max_length=255, blank=True)
    model_used = models.CharField(max_length=100, blank=True)
    youtube_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Audio files (subfolders in MEDIA_ROOT/audio/<dataset_name>)
    audio_file_1 = models.FileField(upload_to=audio_upload_path, blank=True)
    audio_file_2 = models.FileField(upload_to=audio_upload_path, blank=True)

    # Durations in seconds
    audio1_duration = models.FloatField(null=True, blank=True)
    audio2_duration = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.dataset.name})"

    def save(self, *args, **kwargs):
        """
        Overridden to handle audio file durations:

        1) Call super() to save the record (and files).
        2) If audio_file_1 or audio_file_2 is newly uploaded or we have no duration:
             - Attempt to open the file via pydub
             - Compute round(seg.duration_seconds, 2)
             - Update the respective duration field
        3) If updated, call super().save() again with update_fields.

        Raises:
            Exception: If pydub fails to parse the file, duration is set to 0.0.
        """
        # First, do the normal save
        super().save(*args, **kwargs)

        updated = False  # track if we updated any durations

        # Process first file if present and no existing duration
        if self.audio_file_1 and (not self.audio1_duration or self.audio1_duration == 0):
            try:
                path = self.audio_file_1.path
                seg = AudioSegment.from_file(path)
                self.audio1_duration = round(seg.duration_seconds, 2)
                updated = True
            except Exception:
                self.audio1_duration = 0.0

        # Process second file if present and no existing duration
        if self.audio_file_2 and (not self.audio2_duration or self.audio2_duration == 0):
            try:
                path = self.audio_file_2.path
                seg = AudioSegment.from_file(path)
                self.audio2_duration = round(seg.duration_seconds, 2)
                updated = True
            except Exception:
                self.audio2_duration = 0.0

        # If we updated durations, do a partial save
        if updated:
            super().save(update_fields=['audio1_duration', 'audio2_duration'])

    class Meta:
        ordering = ['-created_at']
        # Example: newest entries first
