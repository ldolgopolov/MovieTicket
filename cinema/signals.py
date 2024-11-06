import asyncio
from paypal.standard.models import ST_PP_COMPLETED, ST_PP_DECLINED, ST_PP_CANCELLED
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from django.dispatch import receiver
from django.shortcuts import redirect
from .models import Ticket, Session, User
from tickets.ticket import GetTicket
from cinema.views import send_ticket
import re


@receiver(valid_ipn_received)
def valid_ipn_signal(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        print(f'IPN VALID')
        ids = extract_data(ipn_obj.invoice)
        Ticket.objects.filter(id=ids[1]).update(paid=True)
        user = User.objects.get(id=ids[2])

        session = Session.objects.get(id=ids[0])
        ticket_file = f'popcorntime-{session.movie.title}-{ids[1]}.pdf'.replace(' ', '-').replace(':', '')

        # Ticket Action
        ticket = GetTicket(ticket_file, user.email, session.id, ids[1])
        ticket.create_ticket_file()
        send_ticket(ticket_file, user.email, session.id, ids[1])
        
        User.objects.filter(id=ids[2]).delete()



@receiver(invalid_ipn_received)
def invalid_ipn_signal(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_CANCELLED or ipn_obj.payment_status == ST_PP_DECLINED:
        print('IPN INVALID')
        ids = extract_data(ipn_obj.invoice)
        ticket = Ticket.objects.get(id=ids[1])
        if ticket:
            ticket.delete()
        User.objects.filter(id=ids[2]).delete()


def extract_data(invoice):
    match = re.search(r'(\d+)-(\d+)-(\d+)', invoice)

    session_id = int(match.group(1))
    ticket_id = int(match.group(2))
    user_id = int(match.group(3))
    return session_id, ticket_id, user_id