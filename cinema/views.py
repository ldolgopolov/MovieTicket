from django.shortcuts import render
from django.utils import timezone
from .models import Session

def home(request):
    now = timezone.now()

    Session.objects.filter(start_time__lt=now).delete()

    upcoming_sessions = Session.objects.filter(start_time__gt=now).order_by('start_time')
    context = {'sessions': upcoming_sessions}

    query = request.GET.get('search', '')
    if query:
        sessions = Session.objects.filter(movie__title__icontains=query)
        context = {'sessions': sessions, 'query': query}
    else:
        sessions = Session.objects.all()
    
    return render(request, 'home.html', context)