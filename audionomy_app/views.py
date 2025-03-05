"""
Views for the audionomy_app in the Audionomy Django project.

Each view corresponds to a route defined in urls.py and handles user actions such as:
- Displaying the home page with a list of datasets
- Managing a specific dataset (listing entries, etc.)
- Adding a new audio entry
- Exporting a dataset (placeholder for future logic)

Relevant Models:
- Dataset: Groups multiple AudioEntry objects
- AudioEntry: Holds metadata & file references for an audio track
"""

from django.shortcuts import (
    render, redirect, get_object_or_404
)
from django.http import HttpResponse
from django.urls import reverse
from .models import Dataset, AudioEntry


def home(request):
    """
    Display the home page with all existing Datasets, and allow creating a new one.

    Methods:
    - GET: Renders a template showing the list of datasets.
    - POST: Creates a new Dataset from 'dataset_name' in form data.

    Template:
    - audionomy_app/home.html

    Returns:
        Renders home.html with the context {'datasets': <QuerySet of all Datasets>}
    """
    datasets = Dataset.objects.all().order_by('name')

    if request.method == 'POST':
        dataset_name = request.POST.get('dataset_name', '').strip()
        if dataset_name:
            Dataset.objects.create(name=dataset_name)
        # After creating or skipping, redirect back home
        return redirect('home')

    context = {'datasets': datasets}
    return render(request, 'audionomy_app/home.html', context)


def manage_dataset(request, dataset_id):
    """
    Manage a specific dataset by listing its AudioEntry objects and providing
    links to add new entries or export them.

    Methods:
    - GET: Renders a manage_dataset.html with a table/list of AudioEntry objects.
    - (Optional) Could handle POST if you plan to do inline editing or deletions.

    Template:
    - audionomy_app/manage_dataset.html

    Returns:
        Renders manage_dataset.html with {'dataset': dataset, 'entries': dataset.entries.all()}
        or a 404 if dataset doesn't exist.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    entries = dataset.entries.all().order_by('-created_at')

    context = {
        'dataset': dataset,
        'entries': entries,
    }
    return render(request, 'audionomy_app/manage_dataset.html', context)


def add_entry(request, dataset_id):
    """
    Add a new AudioEntry to a given Dataset, including optional file upload(s).

    Methods:
    - GET: Renders a form to fill out title, prompts, and optionally upload file(s).
    - POST: Processes the form, creating an AudioEntry and assigning any uploaded files.

    Template:
    - audionomy_app/add_entry.html

    Returns:
        Redirects to the manage_dataset page on success, or re-renders the form on GET.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)

    if request.method == 'POST':
        # Gather form fields
        title = request.POST.get('title', '').strip()
        style_prompt = request.POST.get('style_prompt', '').strip()
        exclude_prompt = request.POST.get('exclude_prompt', '').strip()
        model_used = request.POST.get('model_used', '').strip()
        youtube_link = request.POST.get('youtube_link', '').strip()

        file1 = request.FILES.get('audio_file_1')
        file2 = request.FILES.get('audio_file_2')

        # Create the entry
        entry = AudioEntry(
            dataset=dataset,
            title=title,
            style_prompt=style_prompt,
            exclude_style_prompt=exclude_prompt,
            model_used=model_used,
            youtube_link=youtube_link,
        )
        # Assign uploaded files if present
        if file1:
            entry.audio_file_1 = file1
        if file2:
            entry.audio_file_2 = file2

        entry.save()  # triggers pydub-based duration if files are present

        return redirect('manage_dataset', dataset_id=dataset_id)

    # If GET, just show the form
    context = {'dataset': dataset}
    return render(request, 'audionomy_app/add_entry.html', context)


import csv
from django.http import HttpResponse

def export_dataset(request, dataset_id):
    """
    Export dataset entries as a CSV file.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="{dataset.name}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Title", "Style", "Duration", "YouTube Link"])

    for entry in dataset.entries.all():
        writer.writerow([
            entry.title,
            entry.style_prompt or "N/A",
            entry.audio1_duration or "N/A",
            entry.youtube_link or "N/A"
        ])

    return response
