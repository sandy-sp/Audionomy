from django.shortcuts import render, redirect, get_object_or_404
from .models import Dataset, AudioEntry

def home(request):
    datasets = Dataset.objects.all()
    if request.method == 'POST':
        name = request.POST.get('dataset_name', '').strip()
        if name:
            Dataset.objects.create(name=name)
        return redirect('home')
    return render(request, 'audionomy_app/home.html', {'datasets': datasets})
