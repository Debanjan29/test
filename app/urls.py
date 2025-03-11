from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("", views.sendd),#Rest framework
    path("mail/", views.generate_pdf_send_mail),
    path('check-status/', views.checkStatus),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
]