
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg


class CustomUser(models.Model):
    uid = models.AutoField(primary_key=True)  # PK
    owner = models.CharField(max_length=50)
    email = models.EmailField(max_length=50,null=True, blank=True)

    def __str__(self):
        return self.owner
    

class Vehicle(models.Model):
    FUEL_CHOICES = (
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
    )
    Vehicle_choice = (
        ('2W', '2W'),
        ('4W', '4W'),
        ('HDV','Heavy Duty Vehicle'),
    )

    Vehicle_type = models.CharField(max_length=20, choices=Vehicle_choice,default='2W')
    number_plate = models.CharField(max_length=8, primary_key=True)  # PK
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    year = models.IntegerField()
    FuelType = models.CharField(max_length=6, choices=FUEL_CHOICES,default='Petrol')

    def __str__(self):
        return f"Vehicle {self.number_plate} owned by {self.owner}"


class IOT(models.Model):
    iot = models.CharField(max_length=20, primary_key=True)  # PK
    number_plate = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Renamed c_id to owner for clarity


    def __str__(self):
        return f"IoT Device {self.iot} for Vehicle {self.number_plate}"
    

class PollutionEstimate(models.Model):
    id = models.AutoField(primary_key=True)  # PK
    iot = models.ForeignKey(IOT, on_delete=models.CASCADE)  # FK to IOT

    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp when the estimate was calculated

    avg_co = models.FloatField()  # Average CO level in ppm       1
    avg_no2 = models.FloatField()  # Average NO2 level in ppm     2 
    avg_so2 = models.FloatField()  # Average SO2 level in ppm     3
    avg_co2 = models.FloatField()  # Average CO2 level in ppm     4
    #avg_ch4 = models.FloatField()  # Average CH4 level in ppm
    avg_pm = models.FloatField()  # Average PM level in ppm   5
    #avg_nh3 = models.FloatField()  # Average NH3 level in ppm

    finalEstimate=models.FloatField()  #Final weighted avg.

    def __str__(self):
        return f"Pollution Estimate for {self.iot} at {self.timestamp}"


class SensorData(models.Model):
    id = models.AutoField(primary_key=True)  # PK
    iot = models.ForeignKey(IOT, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of when the data was recorded
    co = models.FloatField()  # CO level in ppm
    no2 = models.FloatField()  # NO2 level in ppm
    so2 = models.FloatField()  # SO2 level in ppm
    co2 = models.FloatField()  # CO2 level in ppm
    #ch4 = models.FloatField()  # CH4 level in ppm
    pm = models.FloatField()  # Particular-Matter level in ppm
    #nh3 = models.FloatField()  # NH3 level in ppm
    

    def __str__(self):
        return f"Sensor Data recorded at {self.timestamp} for IoT Device {self.iot.iot}"



@receiver(post_save,sender=SensorData)
def create_pollution_estimate(sender,instance,created, **kwargs):
    if created:
        
        iot_id=instance.iot
        data_count=SensorData.objects.filter(iot=iot_id).count()

        if data_count >= 7:
            # Calculate pollution estimate
            print("Working on Pollution Estimate for {iot_id}")
            calculate_pollution_estimate(iot_id)


def calculate_pollution_estimate(iot_id):
    sensor_data=SensorData.objects.filter(iot=iot_id).order_by('-timestamp')[:5]

    averages = sensor_data.aggregate(
        avg_co=Avg('co'),
        avg_no2=Avg('no2'),
        avg_so2=Avg('so2'),
        avg_co2=Avg('co2'),
        avg_pm=Avg('pm'),
    )

    # Create and save a PollutionEstimate record
    pollution_estimate = PollutionEstimate(
    iot=iot_id,
    avg_co=averages['avg_co'],
    avg_no2=averages['avg_no2'],
    avg_so2=averages['avg_so2'],
    avg_co2=averages['avg_co2'],
    avg_pm=averages['avg_pm'],
    finalEstimate = 0)

    
    pollution_estimate.save()

    return pollution_estimate

# @receiver(post_save,sender=PollutionEstimate)
#  def DeleteSensorData(self,instance,created,**kwargs):
    if created:
        iot_=instance.iot

        SensorData.objects.filter(iot_id=iot_).delete()
#ma '''
