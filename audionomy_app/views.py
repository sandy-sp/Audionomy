from django.shortcuts import render, redirect, get_object_or_404
from .models import Dataset, AudioEntry

def home(request):
    """
    Lists all Datasets and allows creating a new one via POST.
    """
    datasets = Dataset.objects.all()
    if request.method == 'POST':
        name = request.POST.get('dataset_name', '').strip()
        if name:
            Dataset.objects.create(name=name)
        return redirect('home')
    return render(request, 'audionomy_app/home.html', {'datasets': datasets})

def manage_dataset(request, dataset_id):
    """
    Show a dataset's entries, links to add new entries, export, etc.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    entries = dataset.entries.all()
    return render(request, 'audionomy_app/manage_dataset.html', {
        'dataset': dataset,
        'entries': entries,
    })

def add_entry(request, dataset_id):
    """
    For GET: show a form to add a new AudioEntry.
    For POST: create the entry with file uploads.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        # gather other fields...
        audio_file_1 = request.FILES.get('audio_file_1')
        # etc.

        entry = AudioEntry(dataset=dataset, title=title)
        if audio_file_1:
            entry.audio_file_1 = audio_file_1
        # handle second file if needed...
        entry.save()  # triggers DB insertion
        return redirect('manage_dataset', dataset_id=dataset.id)
    
    return render(request, 'audionomy_app/add_entry.html', {'dataset': dataset})

def export_dataset(request, dataset_id):
    """
    Example: produce a ZIP or CSV of the dataset's content. 
    Similar to your old Flask 'export' logic.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id)
    # create CSV or ZIP on the fly, return as HTTP response...
    pass
