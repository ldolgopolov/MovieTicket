from django.shortcuts import render
from .models import Session

def home(request):
    query = request.GET.get('search', '')
    if query:
        sessions = Session.objects.filter(movie__title__icontains=query)
    else:
        sessions = Session.objects.all()
    
    return render(request, 'home.html', {'sessions': sessions, 'query': query})