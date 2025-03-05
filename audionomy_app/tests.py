"""
Unit tests for the Audionomy Django app.

This file includes tests for:
  - Model creation: Dataset and AudioEntry.
  - Audio file upload and duration calculation using pydub.
  - Basic view functionality: home page GET and POST for creating a dataset,
    and managing a dataset.
  - Export endpoints: CSV, JSON, Parquet, and ZIP archive exports.
"""

import io
import zipfile
import pandas as pd

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from pydub import AudioSegment
from .models import Dataset, AudioEntry


class AudionomyModelTests(TestCase):
    def test_dataset_creation(self):
        """
        Test that a Dataset can be created and its fields are properly set.
        """
        dataset = Dataset.objects.create(name="Test Dataset")
        self.assertEqual(dataset.name, "Test Dataset")
        self.assertIsNotNone(dataset.created_at)

    def test_audio_entry_creation_without_file(self):
        """
        Test creating an AudioEntry without any audio files.
        """
        dataset = Dataset.objects.create(name="Test Dataset")
        entry = AudioEntry.objects.create(dataset=dataset, title="Test Audio")
        self.assertEqual(entry.title, "Test Audio")
        self.assertIsNone(entry.audio1_duration)
        self.assertIsNone(entry.audio2_duration)

    def test_audio_entry_file_upload_and_duration(self):
        """
        Test that an AudioEntry with an uploaded file correctly computes its duration.
        This uses a generated 1-second silent audio file.
        """
        dataset = Dataset.objects.create(name="Test Dataset")
        # Generate a 1-second silent audio segment using pydub
        silent_audio = AudioSegment.silent(duration=1000)  # 1000 ms = 1 second
        buffer = io.BytesIO()
        silent_audio.export(buffer, format="mp3")
        buffer.seek(0)
        
        # Create a SimpleUploadedFile with the dummy audio data
        dummy_audio_file = SimpleUploadedFile(
            "test_audio.mp3",
            buffer.read(),
            content_type="audio/mpeg"
        )
        
        # Create AudioEntry with the dummy audio file
        entry = AudioEntry.objects.create(
            dataset=dataset,
            title="Test Audio with File",
            audio_file_1=dummy_audio_file
        )
        entry.refresh_from_db()
        # The duration should be approximately 1.0 second (allowing slight variation)
        self.assertAlmostEqual(entry.audio1_duration, 1.0, places=1)


class AudionomyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')

    def test_home_view_GET(self):
        """
        Test that the home view renders successfully and uses the correct template.
        """
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'audionomy_app/home.html')

    def test_create_dataset_POST(self):
        """
        Test that posting to the home view creates a new Dataset and redirects.
        """
        response = self.client.post(self.home_url, data={'dataset_name': 'New Test Dataset'})
        self.assertEqual(response.status_code, 302)  # expecting a redirect after POST

        # Verify that the dataset exists in the database
        dataset = Dataset.objects.get(name='New Test Dataset')
        self.assertIsNotNone(dataset)

    def test_manage_dataset_view(self):
        """
        Test that the manage_dataset view returns a 200 response and uses the correct template.
        """
        dataset = Dataset.objects.create(name="Test Dataset")
        manage_url = reverse('manage_dataset', args=[dataset.id])
        response = self.client.get(manage_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'audionomy_app/manage_dataset.html')

    def test_export_csv(self):
        """
        Test that the CSV export endpoint returns a CSV file.
        """
        dataset = Dataset.objects.create(name="CSV Test Dataset")
        # Create an entry for export
        AudioEntry.objects.create(dataset=dataset, title="CSV Test Audio")
        export_url = reverse('export_dataset_csv', args=[dataset.id])
        response = self.client.get(export_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_export_json(self):
        """
        Test that the JSON export endpoint returns a JSON file.
        """
        dataset = Dataset.objects.create(name="JSON Test Dataset")
        AudioEntry.objects.create(dataset=dataset, title="JSON Test Audio")
        export_url = reverse('export_dataset_json', args=[dataset.id])
        response = self.client.get(export_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_export_parquet(self):
        """
        Test that the Parquet export endpoint returns a Parquet file.
        """
        dataset = Dataset.objects.create(name="Parquet Test Dataset")
        AudioEntry.objects.create(dataset=dataset, title="Parquet Test Audio")
        export_url = reverse('export_dataset_parquet', args=[dataset.id])
        response = self.client.get(export_url)
        self.assertEqual(response.status_code, 200)
        # Parquet export content type is set to application/octet-stream
        self.assertEqual(response['Content-Type'], 'application/octet-stream')
        # Optionally, try reading the parquet content to ensure it loads as a DataFrame.
        buffer = io.BytesIO(response.content)
        df = pd.read_parquet(buffer)
        self.assertGreater(len(df), 0)

    def test_export_audio_zip(self):
        """
        Test that the ZIP export endpoint returns a ZIP archive containing audio files.
        """
        dataset = Dataset.objects.create(name="ZIP Test Dataset")
        
        # Create a dummy audio file for the entry.
        silent_audio = AudioSegment.silent(duration=1000)  # 1 second silence
        buffer = io.BytesIO()
        silent_audio.export(buffer, format="mp3")
        buffer.seek(0)
        dummy_audio_file = SimpleUploadedFile("zip_test_audio.mp3", buffer.read(), content_type="audio/mpeg")
        
        AudioEntry.objects.create(dataset=dataset, title="ZIP Test Audio", audio_file_1=dummy_audio_file)
        export_url = reverse('export_audio_zip', args=[dataset.id])
        response = self.client.get(export_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        
        # Verify that the ZIP archive is valid and contains at least one file.
        zip_buffer = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            file_list = zf.namelist()
            self.assertGreater(len(file_list), 0)
