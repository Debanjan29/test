
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

    number_plate=IOT.objects.get(iot=iot_id).number_plate
    vehicleType=Vehicle.objects.get(number_plate=number_plate).Vehicle_type
    fuelType=Vehicle.objects.get(number_plate=number_plate).FuelType
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
    avg_co=averages['avg_co']*28.01/24.45,# PPM TO mg/m3
    avg_no2=averages['avg_no2']*46.01/24.45,
    avg_so2=averages['avg_so2'],  #Unit in ppm as per Standards
    avg_co2=averages['avg_co2']*44.01/24.45,
    avg_pm=averages['avg_pm'],
    finalEstimate = PollutionCalculation(averages['avg_co']*28.01/24.45,averages['avg_no2']*46.01/24.45,averages['avg_so2'],averages['avg_co2']*44.01/24.45,averages['avg_pm'],vehicleType,fuelType)
    )

    
    pollution_estimate.save()

    return pollution_estimate


def PollutionCalculation(co,no2,so2,co2,pm,vehicleType,fuelType):
    if(vehicleType=='2W' and fuelType=='Petrol'):
        #2W
        if(co>2000 or no2>100 or so2>10 or co2>3170 or pm>200):
            return 1

    elif(vehicleType=='2W' and fuelType=='Diesel'):
        if(co>2000 or no2>100 or so2>10 or co2>3140 or pm>200):
            return 1


    elif(vehicleType=='4W' and fuelType=='Petrol'):
        if(co>1000 or no2>60 or so2>10 or co2>3170 or pm>4.5):
            return 1



    elif(vehicleType=='4W' and fuelType=='Diesel'):
        if(co>500 or no2>80 or so2>10 or co2>3140 or pm>4.5):
            return 1


    elif(vehicleType=='HDV'):
        if(co>15000 or no2>3500 or so2>10 or co2>3140 or pm>20):
            return 1

@receiver(post_save, sender=PollutionEstimate)
def auto_generate_challan(sender, instance, created, **kwargs):
    if created and instance.finalEstimate == 1:
        # ✅ Generate Fine
        fine_amount = 1000
        challan = Challan.objects.create(
            iot=instance.iot,
            amount=fine_amount
        )

        # ✅ Send Email
        challan.send_email_notification()



# @receiver(post_save,sender=PollutionEstimate)
# def DeleteSensorData(self,instance,created,**kwargs):
#     if created:
#         iot_=instance.iot

#         SensorData.objects.filter(iot_id=iot_).delete()



#ma '''



from django.db import models
from django.core.mail import EmailMessage
from io import BytesIO
from reportlab.pdfgen import canvas
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class Challan(models.Model):
    iot = models.ForeignKey('IOT', on_delete=models.CASCADE)
    amount = models.FloatField()
    paid = models.BooleanField(default=False)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Challan for {self.iot} - Paid: {self.paid}"

    def generate_payment_link(self):
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': f"Pollution Fine for {self.iot}",
                    },
                    'unit_amount': int(self.amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{settings.SITE_URL}/payment-success/?challan_id={self.id}",
            cancel_url=f"{settings.SITE_URL}/payment-cancel/",
        )
        return checkout_session.url

    # def generate_pdf_receipt(self):
    #     buffer = BytesIO()
    #     p = canvas.Canvas(buffer)
    #     p.drawString(100, 800, f"Challan Receipt")
    #     p.drawString(100, 780, f"Vehicle Number: {self.iot.number_plate}")
    #     p.drawString(100, 760, f"Amount: ₹{self.amount}")
    #     p.drawString(100, 740, f"Issued Date: {self.issued_at}")
    #     p.drawString(100, 720, f"Payment Status: {'Paid' if self.paid else 'Unpaid'}")
    #     p.drawString(100, 700, f"Payment Link: {self.generate_payment_link()}")
    #     p.showPage()
    #     p.save()
    #     buffer.seek(0)
    #     return buffer

    def send_email_notification(self):
        # Generate PDF and Payment Link
        #pdf_buffer = self.generate_pdf_receipt()
        payment_url = self.generate_payment_link()

        No_Plate=IOT.objects.get(iot=self.iot).number_plate
        # Email Content
        message = f"""
        Your vehicle {self.iot.number_plate} has exceeded the pollution threshold.
        A fine of ₹{self.amount} has been generated.
        Please pay the fine using the link below:

        Payment Link: {payment_url}

        Thank you for your cooperation.
        """

        # Send Email with PDF
        email = EmailMessage(
            'Pollution Fine Notification',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.iot.owner.email]
        )

        #email.attach(f'challan_{self.id}.pdf', pdf_buffer.getvalue(), 'application/pdf')
        email.send()
