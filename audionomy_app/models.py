"""
Models for the audionomy_app.

This module defines two primary models:
  1. Dataset: Groups a set of audio entries under one name.
  2. AudioEntry: Represents a specific audio item with associated metadata and up to two audio files,
     along with additional fields like lyrics, persona, and an optional uploaded sample file.

Features:
  - Audio files are organized under: media/audio/<dataset_name>/<sanitized_filename>
  - A separate sample file (if provided) is organized under: media/sample/<dataset_name>/<sanitized_filename>
  - On save, audio durations are computed using pydub.
  - In case of unsupported formats or errors, durations default to 0.0, with errors logged.
"""

import os
import re
import logging
from pathlib import Path

from django.db import models
from pydub import AudioSegment

# Set up a module-level logger
logger = logging.getLogger(__name__)


class Dataset(models.Model):
    """
    Represents a named group of audio entries.

    Fields:
      - name (str, unique): The dataset's name, e.g., 'Instrumentals 2025'.
      - created_at (DateTime): Automatically set to the creation time.
    """
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


def audio_upload_path(instance, filename):
    """
    Generate a safe file upload path for audio files.

    This function:
      1. Removes any characters outside [a-zA-Z0-9._-].
      2. Uses the dataset's name (spaces replaced with underscores).
      3. Returns a relative path: "audio/<dataset_name>/<safe_filename>".

    Args:
      - instance (AudioEntry): The model instance being saved.
      - filename (str): Original filename from the upload.

    Returns:
      - str: Relative file path.
    """
    safe_filename = re.sub(r"[^a-zA-Z0-9._-]+", "", filename)
    dataset_name = instance.dataset.name.replace(" ", "_")
    return f"audio/{dataset_name}/{safe_filename}"


def sample_upload_path(instance, filename):
    """
    Generate a safe file upload path for sample audio files.

    This function:
      1. Sanitizes the filename.
      2. Uses the dataset's name (spaces replaced with underscores).
      3. Returns a relative path: "sample/<dataset_name>/<safe_filename>".

    Args:
      - instance (AudioEntry): The model instance being saved.
      - filename (str): Original filename from the upload.

    Returns:
      - str: Relative file path for sample files.
    """
    safe_filename = re.sub(r"[^a-zA-Z0-9._-]+", "", filename)
    dataset_name = instance.dataset.name.replace(" ", "_")
    return f"sample/{dataset_name}/{safe_filename}"


class AudioEntry(models.Model):
    """
    Represents a single audio entry within a Dataset, storing metadata, audio files,
    and additional details for comprehensive dataset creation.

    Fields:
      - dataset (ForeignKey): Links to a Dataset (CASCADE deletion).
      - title (str): Title of the audio piece.
      - style_prompt (str): Style or mood prompt for generating audio.
      - exclude_style_prompt (str): Description of styles to exclude.
      - model_used (str): The AI model or generation method used.
      - youtube_link (URLField): Optional external YouTube reference.
      - lyrics (TextField): Optional lyrics for the audio piece.
      - persona (CharField): Optional persona information.
      - uploaded_sample (FileField): Optional sample audio file to mimic.
      - created_at (DateTime): Automatically set creation datetime.
      - audio_file_1, audio_file_2 (FileField): Uploaded audio files.
      - audio1_duration, audio2_duration (FloatField): Computed durations in seconds.
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
    lyrics = models.TextField(blank=True)
    persona = models.CharField(max_length=255, blank=True)
    uploaded_sample = models.FileField(upload_to=sample_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Audio files (stored under media/audio/<dataset_name>)
    audio_file_1 = models.FileField(upload_to=audio_upload_path, blank=True)
    audio_file_2 = models.FileField(upload_to=audio_upload_path, blank=True)

    # Durations in seconds
    audio1_duration = models.FloatField(null=True, blank=True)
    audio2_duration = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.dataset.name})"

    def save(self, *args, **kwargs):
        """
        Overridden save method to compute audio durations after file upload.

        Process:
          1. Save the instance to ensure file fields are available.
          2. For each audio file (if present and duration not set), attempt to compute the duration.
          3. In case of an error (e.g., unsupported format), log the error and default the duration to 0.0.
          4. If any duration is updated, perform a partial save to update only the duration fields.
        """
        # First, perform the standard save.
        super().save(*args, **kwargs)

        updated = False  # Flag to track if any duration was updated

        # Process first audio file.
        if self.audio_file_1 and (not self.audio1_duration or self.audio1_duration == 0):
            try:
                path = self.audio_file_1.path
                seg = AudioSegment.from_file(path)
                self.audio1_duration = round(seg.duration_seconds, 2)
                updated = True
            except Exception as e:
                logger.error(f"Error processing audio_file_1 for entry '{self.title}': {e}")
                self.audio1_duration = 0.0

        # Process second audio file.
        if self.audio_file_2 and (not self.audio2_duration or self.audio2_duration == 0):
            try:
                path = self.audio_file_2.path
                seg = AudioSegment.from_file(path)
                self.audio2_duration = round(seg.duration_seconds, 2)
                updated = True
            except Exception as e:
                logger.error(f"Error processing audio_file_2 for entry '{self.title}': {e}")
                self.audio2_duration = 0.0

        # If any duration was updated, save the changes.
        if updated:
            super().save(update_fields=['audio1_duration', 'audio2_duration'])

    class Meta:
        ordering = ['-created_at']
        # Newest entries first
