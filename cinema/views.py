from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, FileResponse
from secret import Config
from .models import Session, Ticket, User
from .forms import UserInfoForm
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
import random
from datetime import datetime
import os

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


def user_form(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.method == 'POST':
        form = UserInfoForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            birth_date = form.cleaned_data['birth_date']
            email = form.cleaned_data['email']

            request.session['first_name'] = first_name
            request.session['last_name'] = last_name
            request.session['birth_date'] = str(birth_date)
            request.session['email'] = email
            
            user = User.objects.create(first_name=first_name, last_name=last_name, birth_date=str(birth_date), email=email)
            request.session['user_id'] = user.id
            return redirect('choose_seat', session_id=session.id)
    else:
        form = UserInfoForm()

    context = {
        'session': session,
        'form': form
    }
    return render(request, 'user_form.html', context)


def choose_seat(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    hall = session.hall
    
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)

    booked_tickets = Ticket.objects.filter(session=session)
    booked_seats = {f"{ticket.seat_row}-{ticket.seat_number}" for ticket in booked_tickets}

    rows = list(range(1, hall.rows + 1))
    seats_per_row = list(range(1, hall.seats_per_row + 1))

    if request.method == 'POST':
        selected_row = request.POST.get('row')
        selected_seat = request.POST.get('seat')
        
        if not selected_row or not selected_seat:
            return render(request, 'choose_seat.html', {
                'session': session,
                'rows': rows,
                'seats_per_row': seats_per_row,
                'booked_seats': booked_seats,
                'error_message': "Lūdzu, izvēlieties vietu!"
            })
        
        selected_row = int(request.POST.get('row'))
        selected_seat = int(request.POST.get('seat'))
        
        if f"{selected_row}-{selected_seat}" in booked_seats:
            return render(request, 'choose_seat.html', {
                'session': session,
                'rows': rows,
                'seats_per_row': seats_per_row,
                'booked_seats': booked_seats,
                'error_message': "Vieta jau ir rezervēta!"
            })

        ticket = Ticket.objects.create(
            user=user,
            session=session,
            seat_row=selected_row,
            seat_number=selected_seat,
            price=session.price,
            expiration_time = session.start_time
        )
        session.viewers += 1
        Session.objects.filter(id=session_id).update(viewers=session.viewers)

        request.session['ticket_id'] = ticket.id
        slug = f'{random.randint(10000, 99999)}-{user_id}'
        return redirect('payment', session_id=session.id, slug=slug)

    return render(request, 'choose_seat.html', {
        'session': session,
        'rows': rows,
        'seats_per_row': seats_per_row,
        'booked_seats': booked_seats,
    })


def payment(request, session_id, slug):
    session = Session.objects.get(id=session_id)
    ticket_id = request.session.get('ticket_id')
    ticket = Ticket.objects.get(id=ticket_id)

    paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': f'{session.price}',
            "item_name": f"Ticket {session.movie.title}",
            'movie': f'{session.movie.title}',
            'invoice': f'{session.id}-{ticket.id}-{ticket.user.id}',
            'currency_code': 'USD',
            'notify_url': f'https://{Config.HOST}{reverse(f"paypal-ipn")}',
            "return": f'https://{Config.HOST}{reverse("paypal-return")}',
            "cancel_return": f'https://{Config.HOST}{reverse("paypal-cancel")}',
        }
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {'form': form, 
               'slug': slug, 
               'movie': session.movie.title, 
               'amount': session.price,
               'session': session}
    return render(request, 'payment.html', context)

def paypal_return(request):
    return render(request, 'payment_success.html')


def paypal_cancel(request):
    message = messages.error(request, "Your order has been cancelled")
    context = {'message': message}
    return render(request, 'payment_cancel.html', context)


def download_page(request, session_id, ticket_file):
    session = get_object_or_404(Session, id=session_id)
    context = {'session': session, 
               'ticket_file': ticket_file}
    return render(request, 'download_page.html', context)

def download_ticket(request, ticket_file):
    file_path = os.path.join(settings.BASE_DIR, f'/tickets/{ticket_file}')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as pdf:
            response = FileResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{ticket_file}"'
            return response
    else:
        raise Http404("Invalid file name")
    



# Ticket Action
def send_ticket(file_name, customer_mail, session_id, ticket_id):
    session = Session.objects.get(id=session_id)
    ticket = Ticket.objects.get(id=ticket_id)
    context = {
        "session": session,
        "ticket": ticket,
        "year": datetime.fromisoformat(str(session.start_time)).year,
        "day": datetime.fromisoformat(str(session.start_time)).day,
        "month": datetime.fromisoformat(str(session.start_time)).month,
        "hour": datetime.fromisoformat(str(session.start_time)).hour,
        "minute": datetime.fromisoformat(str(session.start_time)).minute,
    }

    html_body = render_to_string("mail_template.html", context)
    msg = EmailMultiAlternatives(subject=f"Apsveicam ar biļešu iegādi! #{ticket_id}", to=[customer_mail])

    msg.attach_file(f"tickets/{file_name}")
    msg.attach_alternative(html_body, "text/html")

    image_path = os.path.join(settings.MEDIA_ROOT, f"{session.movie.image.url}".replace("/media/", ""))
    with open(image_path, 'rb') as img:
        mime_image = MIMEImage(img.read())
        mime_image.add_header('Content-ID', '<image_id>')
        msg.attach(mime_image)

    qr_code_path = os.path.join(settings.BASE_DIR, f"tickets\\qrcodes\\{ticket_id}_qrcode.png")
    with open(qr_code_path, 'rb') as img:
        mime_image = MIMEImage(img.read())
        mime_image.add_header('Content-ID', '<qrcode_id>')
        msg.attach(mime_image)

    msg.send()
