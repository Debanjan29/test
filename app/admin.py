from django.contrib import admin
from django.contrib import admin
from .models import CustomUser,Vehicle,SensorData,PollutionEstimate,IOT,Challan

admin.site.register(Challan)
admin.site.register(CustomUser)
admin.site.register(Vehicle)
admin.site.register(IOT)
admin.site.register(PollutionEstimate)
admin.site.register(SensorData)


# Register your models here.'''
