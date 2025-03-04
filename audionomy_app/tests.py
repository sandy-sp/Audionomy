"""
Unit tests for the Audionomy Django app.

This file includes tests for:
  - Model creation: Dataset and AudioEntry.
  - Audio file upload and duration calculation using pydub.
  - Basic view functionality: home page GET and POST for creating a dataset,
    and managing a dataset.
"""

import io
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
        # Refresh from DB to update fields from the overridden save method
        entry.refresh_from_db()
        
        # The duration should be approximately 1.0 second (allowing for slight variation)
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
