from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("", views.data_view),
    path("api/record-sensor-data/", views.data_view),
    path('api/data',views.data_view , name='data-receive'),
    path('',views.data_view , name='data-rec'),
]