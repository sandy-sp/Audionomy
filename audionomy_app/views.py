"""
Views for the Audionomy Django project.

Handles:
- Displaying the home page and managing datasets
- Adding, editing, and deleting audio entries
- Exporting dataset data as CSV

Models:
- Dataset: A collection of audio entries
- AudioEntry: Individual entries with metadata and audio files
"""

from django.shortcuts import (
    render, redirect, get_object_or_404
)
from django.http import HttpResponse
from django.urls import reverse
from .models import Dataset, AudioEntry
from .forms import AudioEntryForm
import csv


def home(request):
    """
    Display the home page with a list of datasets and allow creating a new one.

    Methods:
    - GET: Show the list of datasets.
    - POST: Create a new dataset with a given name.

    Returns:
        Renders home.html with {'datasets': <QuerySet of all Datasets>}
    """
    datasets = Dataset.objects.all().order_by('name')

    if request.method == 'POST':
        dataset_name = request.POST.get('dataset_name', '').strip()
        if dataset_name:
            dataset, created = Dataset.objects.get_or_create(name=dataset_name)
        return redirect('home')

    context = {'datasets': datasets}
    return render(request, 'audionomy_app/home.html', context)


def manage_dataset(request, dataset_id):
    """
    View and manage a specific dataset.

    Methods:
    - GET: Show dataset details, list of entries, and actions (Add Entry, Export, Delete).

    Returns:
        Renders manage_dataset.html with {'dataset': dataset, 'entries': dataset.entries.all()}.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    entries = dataset.entries.all().order_by('-created_at')
    datasets = Dataset.objects.all().order_by('name')  # Sidebar fix

    context = {
        'dataset': dataset,
        'entries': entries,
        'datasets': datasets,  # Sidebar datasets
    }
    return render(request, 'audionomy_app/manage_dataset.html', context)


def add_entry(request, dataset_id):
    """
    Add a new AudioEntry to a dataset.

    Methods:
    - GET: Show the form to add a new entry.
    - POST: Process form submission and create the entry.

    Returns:
        Redirects to the dataset management page upon successful submission.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    datasets = Dataset.objects.all().order_by('name')  # Sidebar fix

    if request.method == 'POST':
        form = AudioEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.dataset = dataset
            entry.save()
            return redirect('manage_dataset', dataset_id=dataset.id)
    else:
        form = AudioEntryForm()

    context = {'dataset': dataset, 'form': form, 'datasets': datasets}
    return render(request, 'audionomy_app/add_entry.html', context)

from django.contrib import messages

def delete_entry(request, entry_id):
    """
    Delete an audio entry from a dataset.
    """
    entry = get_object_or_404(AudioEntry, id=entry_id)
    dataset_id = entry.dataset.id

    if request.method == "POST":
        entry.delete()
        messages.success(request, "Entry deleted successfully.")
        return redirect("manage_dataset", dataset_id=dataset_id)

    return render(request, "audionomy_app/confirm_delete.html", {"entry": entry})

def export_dataset(request, dataset_id):
    """
    Export dataset entries as a CSV file.

    Returns:
        CSV file with dataset details.
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

from django.shortcuts import render, redirect, get_object_or_404
from .models import AudioEntry
from .forms import AudioEntryForm

def edit_entry(request, entry_id):
    """
    Edit an existing AudioEntry.
    
    Methods:
    - GET: Show a form pre-filled with existing data.
    - POST: Update entry details upon form submission.
    
    Returns:
        Redirects to dataset management page after saving changes.
    """
    entry = get_object_or_404(AudioEntry, id=entry_id)
    dataset_id = entry.dataset.id
    datasets = Dataset.objects.all().order_by('name')  # Sidebar fix

    if request.method == "POST":
        form = AudioEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("manage_dataset", dataset_id=dataset_id)
    else:
        form = AudioEntryForm(instance=entry)

    return render(request, "audionomy_app/edit_entry.html", {"form": form, "entry": entry, "datasets": datasets})
