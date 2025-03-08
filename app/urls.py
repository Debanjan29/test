from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("", views.sendd),#Rest framework
    path("dashboard/", views.dashboard),
     path('register/', views.register),
     path('login/', views.login_view),
     path('logout/', views.logout_view),
    path("api/record-sensor-data/", views.send),  
    #path('api/data',views.data_view , name='data-receive'),
    path('api/rsd/',views.receive_sensor_data , name='data-rec'),
    path('api/check-status/',views.checkStatus),
]