# audionomy_app/models.py

from django.db import models
from django.conf import settings
from django.core.files import File
from pydub import AudioSegment
import re
import os
from pathlib import Path


class Dataset(models.Model):
    """
    A Dataset groups a set of audio entries under one name.
    Example: 'MyInstrumentalCollection'.
    """
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


def audio_upload_path(instance, filename):
    """
    A custom function to define where audio files are uploaded.
    We sanitize the filename, then store it under media/audio/<dataset_name>/.
    """
    # remove any weird chars from filename
    safe_filename = re.sub(r"[^a-zA-Z0-9._-]+", "", filename)
    dataset_name = instance.dataset.name.replace(" ", "_")
    return f"audio/{dataset_name}/{safe_filename}"


class AudioEntry(models.Model):
    """
    Represents a single audio entry in a dataset.
    Each entry can store up to two audio files (e.g., different versions or formats).
    We'll compute durations automatically after saving.
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

    # Audio files, storing in subfolders of MEDIA_ROOT/audio/<dataset>/
    audio_file_1 = models.FileField(upload_to=audio_upload_path, blank=True)
    audio_file_2 = models.FileField(upload_to=audio_upload_path, blank=True)

    # Duration fields
    audio1_duration = models.FloatField(null=True, blank=True)
    audio2_duration = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.dataset.name})"

    def save(self, *args, **kwargs):
        """
        Overrides the default save to:
          1) Actually store the file(s).
          2) Compute durations with pydub, if files are present.
        """
        super().save(*args, **kwargs)

        # After the main save, compute durations if files exist
        updated = False  # track if we need a 2nd save

        if self.audio_file_1 and (not self.audio1_duration or self.audio1_duration == 0):
            try:
                path = self.audio_file_1.path  # local path
                seg = AudioSegment.from_file(path)
                self.audio1_duration = round(seg.duration_seconds, 2)
                updated = True
            except Exception:
                self.audio1_duration = 0.0

        if self.audio_file_2 and (not self.audio2_duration or self.audio2_duration == 0):
            try:
                path = self.audio_file_2.path
                seg = AudioSegment.from_file(path)
                self.audio2_duration = round(seg.duration_seconds, 2)
                updated = True
            except Exception:
                self.audio2_duration = 0.0

        # If we updated durations, save again
        if updated:
            super().save(update_fields=['audio1_duration', 'audio2_duration'])


    class Meta:
        ordering = ['-created_at']  # newest entries first, for example
