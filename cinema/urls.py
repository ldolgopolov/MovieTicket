from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
import os


urlpatterns = [
    path('', views.home, name='home'),
    path('user-form/<int:session_id>/', views.user_form, name='user_form'),
    path('choose_seat/<int:session_id>/', views.choose_seat, name='choose_seat'),
    path('payment/<int:session_id>/<slug:slug>/', views.payment, name='payment'),
    path('paypal-return/', views.paypal_return, name='paypal-return'),
    path('paypal-cancel/', views.paypal_cancel, name='paypal-cancel'),
    path('download_page/<int:session_id>/<str:ticket_file>/', views.download_page, name='download_page'),
    path('download_ticket/<str:ticket_file>/', views.download_ticket, name='download_ticket'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)