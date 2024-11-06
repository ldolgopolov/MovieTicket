from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from cinema.models import Session, Ticket
import os
from datetime import datetime
from django.conf import settings
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import utils


class GetTicket():
    def __init__(self, file_name, mail, session_id, ticket_id):
        self.file_name = file_name
        self.customer_mail = mail
        self.session_id = session_id
        self.ticket_id = ticket_id

    def render_html(self, html_content, context):
        for key, value in context.items():
            html_content = html_content.replace(f"{{{{ {key} }}}}", f"{value}")
        return html_content

    def create_ticket_file(self):
        file_path = f"tickets/{self.file_name}"
        session = Session.objects.get(id=self.session_id)
        ticket = Ticket.objects.get(id=self.ticket_id)
        self.generate_qrcode()

        context = {
            "session": session,
            "ticket": ticket,
            "year": datetime.fromisoformat(str(session.start_time)).year,
            "day": datetime.fromisoformat(str(session.start_time)).day,
            "month": datetime.fromisoformat(str(session.start_time)).month,
            "hour": datetime.fromisoformat(str(session.start_time)).hour,
            "minute": datetime.fromisoformat(str(session.start_time)).minute,
            'image_url': os.path.join(settings.MEDIA_ROOT, f"{session.movie.image.url}".replace("/media/", "")),
            "qrcode_url": os.path.join(settings.BASE_DIR, f"tickets\\qrcodes\\{self.ticket_id}_qrcode.png"),
        }
        
        html_string = render_to_string('ticket_template.html', context)

        with open(file_path, "wb") as pdf_file:
            pisa.CreatePDF(html_string.encode('utf-8'), dest=pdf_file)

    
    def generate_qrcode(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=30,
            border=4,
        )
        file_path = f'{os.path.dirname(os.path.abspath(__file__))}\\qrcodes\\{self.ticket_id}_qrcode.png'
        data = f'popcorntime-{self.ticket_id}'
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="#f0f0f0")

        img.save(file_path)

    