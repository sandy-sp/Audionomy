from django import forms
from .models import AudioEntry

class AudioEntryForm(forms.ModelForm):
    class Meta:
        model = AudioEntry
        fields = ["title", "style_prompt", "exclude_style_prompt", "model_used", "audio_file_1", "audio_file_2"]
