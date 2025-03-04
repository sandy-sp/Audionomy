from django.db import models

class Dataset(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AudioEntry(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='entries')
    title = models.CharField(max_length=255)
    audio_file_1 = models.FileField(upload_to='audio/', blank=True)
    # ... etc ...
