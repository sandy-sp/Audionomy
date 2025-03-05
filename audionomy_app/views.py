"""
Views for the Audionomy Django project.

Handles:
- Displaying the home page and managing datasets.
- Adding, editing, and deleting audio entries.
- Exporting dataset data as CSV, JSON, Parquet, and a ZIP archive of audio files.

Models:
- Dataset: A collection of audio entries.
- AudioEntry: Individual entries with metadata and audio files.
"""

import io
import csv
import zipfile

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.core import serializers
import pandas as pd

from .models import Dataset, AudioEntry
from .forms import AudioEntryForm


def home(request):
    """
    Display the home page with a list of datasets and allow creating a new one.
    """
    datasets = Dataset.objects.all().order_by('name')

    if request.method == 'POST':
        dataset_name = request.POST.get('dataset_name', '').strip()
        if dataset_name:
            Dataset.objects.get_or_create(name=dataset_name)
        return redirect('home')

    context = {'datasets': datasets}
    return render(request, 'audionomy_app/home.html', context)


def manage_dataset(request, dataset_id):
    """
    View and manage a specific dataset.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    entries = dataset.entries.all().order_by('-created_at')
    # Fetch all datasets for the sidebar.
    all_datasets = Dataset.objects.all().order_by('name')

    context = {
        'dataset': dataset,
        'entries': entries,
        'datasets': all_datasets,
    }
    return render(request, 'audionomy_app/manage_dataset.html', context)


def add_entry(request, dataset_id):
    """
    Add a new AudioEntry to a dataset.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    all_datasets = Dataset.objects.all().order_by('name')

    if request.method == 'POST':
        form = AudioEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.dataset = dataset
            entry.save()
            return redirect('manage_dataset', dataset_id=dataset.id)
    else:
        form = AudioEntryForm()

    context = {'dataset': dataset, 'form': form, 'datasets': all_datasets}
    return render(request, 'audionomy_app/add_entry.html', context)


def delete_entry(request, entry_id):
    """
    Delete an audio entry from a dataset.
    """
    entry = get_object_or_404(AudioEntry, id=entry_id)
    dataset_id = entry.dataset.id

    if request.method == "POST":
        entry.delete()
        # Optionally, add a success message here.
        return redirect("manage_dataset", dataset_id=dataset_id)

    return render(request, "audionomy_app/confirm_delete.html", {"entry": entry})


def edit_entry(request, entry_id):
    """
    Edit an existing AudioEntry.
    """
    entry = get_object_or_404(AudioEntry, id=entry_id)
    dataset_id = entry.dataset.id
    all_datasets = Dataset.objects.all().order_by('name')

    if request.method == "POST":
        form = AudioEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("manage_dataset", dataset_id=dataset_id)
    else:
        form = AudioEntryForm(instance=entry)

    return render(request, "audionomy_app/edit_entry.html", {"form": form, "entry": entry, "datasets": all_datasets})


def export_dataset(request, dataset_id):
    """
    Export dataset entries as a CSV file.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="{dataset.name}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Title", "Style Prompt", "Exclude Style", "Model Used", "Duration (s)", "YouTube Link"])

    for entry in dataset.entries.all():
        writer.writerow([
            entry.title,
            entry.style_prompt or "N/A",
            entry.exclude_style_prompt or "N/A",
            entry.model_used or "N/A",
            entry.audio1_duration or "N/A",
            entry.youtube_link or "N/A"
        ])

    return response


def export_dataset_json(request, dataset_id):
    """
    Export dataset entries as a JSON file.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    data = serializers.serialize('json', dataset.entries.all())
    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{dataset.name}.json"'
    return response


def export_dataset_parquet(request, dataset_id):
    """
    Export dataset entries as a Parquet file.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    # Convert queryset values to a DataFrame
    entries = dataset.entries.all().values(
        "title", "style_prompt", "exclude_style_prompt", "model_used",
        "audio1_duration", "youtube_link", "created_at"
    )
    df = pd.DataFrame(list(entries))
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{dataset.name}.parquet"'
    return response


def export_audio_zip(request, dataset_id):
    """
    Export all audio files from a dataset as a ZIP archive.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for entry in dataset.entries.all():
            for field in ['audio_file_1', 'audio_file_2']:
                file_field = getattr(entry, field)
                if file_field:
                    try:
                        # Write file into the ZIP using a folder per entry title.
                        zip_file.write(file_field.path, arcname=f"{entry.title}/{file_field.name}")
                    except Exception as e:
                        # Log error if file cannot be read.
                        print(f"Error adding file {file_field.name} from entry '{entry.title}': {e}")
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{dataset.name}_audio.zip"'
    return response
