from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
import json
from datetime import datetime, timedelta, timezone
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import SensorData
from .models import IOT
from .models import Vehicle, PollutionEstimate
#from app.models import RTOUser
from .serializer import SensorDataSerializer



from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import FileResponse
from reportlab.pdfgen import canvas
import io


def check_Status(request):
    if request.method=='POST':
        data=request.data
        iot_id=data.get('iot')
        if(IOT.objects.contains(iot=iot_id)):
            return 'registered'
    return 'IOT_id_not_exist'
     

def generate_pdf_send_mail(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    f='test'
    # Draw things on the PDF. Here's where the PDF generation happens.
    p.drawString(100, 100, "Hello, World!")
    p.drawString(100, 800, "This is your PDF Receipt")
    p.drawString(100, 780, f"Message: {f}")
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # File response
    buffer.seek(0)

    email_Obj=EmailMessage(
        'Subject here',#Title
        'Here is the message from Django.',#Message
        'settings.EMAIL_HOST_USER',#From
        ["debanjanbhatt29@gmail.com"],
)
    email_Obj.attach('receipt.pdf', buffer.getvalue(), 'application/pdf')   
    email_Obj.send()
    return FileResponse(buffer, as_attachment=True, filename='receipt.pdf')
#@csrf_exempt

# def sendMail(request):
#     email_Obj=EmailMessage(
#         'Subject here',#Title
#         'Here is the message from Django.',#Message
#         'settings.EMAIL_HOST_USER',#From
#         ["debanjanbhatt29@gmail.com"],
#     fail_silently=False,)
#     email_Obj.attach('receipt.pdf', buffer.getvalue(), 'application/pdf')
#     return JsonResponse({"status": "success", "message": "Mail sent!"})


@api_view(['POST'])
def checkStatus(request):
        
        data=json.loads(request.body)
        iot_id = data.get('iot')
        iot_device = IOT.objects.filter(iot=iot_id).first()

        if not iot_device:
            return Response({"response": "IOT_id_not_exist"}, status=status.HTTP_200_OK)

        else:

            no_plate=IOT.objects.get(iot=iot_id)
            # Calculate the next data collection date
            last_data = PollutionEstimate.objects.filter(iot=iot_id).order_by('-timestamp').first()

            if last_data and last_data.timestamp:
                next_due_date = last_data.timestamp + timedelta(days=180)
            else:
                next_due_date = Vehicle.objects.get(number_plate=no_plate).year  # Use initial assigned date if no data exists

            current_date = timezone.now().date()

            if current_date >= next_due_date:
                    return Response("registered|yes", status=status.HTTP_200_OK)
            else:
                   return Response("registered|no", status=status.HTTP_200_OK)
  
            

        


@api_view(['POST'])
def sendd(request):  #USING REST FRAMEWORK

    serializer=SensorDataSerializer(data=request.data)

    print(request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "success", "message": "Data saved"}, status=status.HTTP_201_CREATED)
    else:
        # Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET','POST'])
def receive_sensor_data(request):
    # Get the data sent from the ESP32
    sensor_data = request.data
    
    # Print the received data in terminal
    print("Received Sensor Data:", sensor_data)
    
    # Example of how to extract individual values (adjust these fields based on actual ESP32 data format)
    mac_address = sensor_data.get('mac_address')
    co = sensor_data.get('co')
    nox = sensor_data.get('nox')
    nh3 = sensor_data.get('nh3')
    co2 = sensor_data.get('co2')
    benzene = sensor_data.get('benzene')
    sulphide = sensor_data.get('sulphide')
    ch4 = sensor_data.get('ch4')
    butane = sensor_data.get('butane')

    print(mac_address)
    print(co)
    print(nox)
    print(butane)
    # Print these individual values in terminal
    #print(f"MAC Address: {mac_address}, CO: {co}, NOx: {nox}, NH3: {nh3}, CO2: {co2}, Benzene: {benzene}, Sulphide: {sulphide}, CH4: {ch4}, Butane: {butane}")
    
    # Send back a success response to ESP32
    if(sensor_data):
        return JsonResponse({"status": "success", "message": "Data received!","mac":"dd"})
    else:
        return JsonResponse({"not recived":"failed"})




@csrf_exempt
def send(request):        #Using just django
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received data:", data)

            # Extracting data safely
            mac_address = data.get('mac_address')
            co = data.get('co')
            no2 = data.get('nox')
            co2 = data.get('co2')
            sulphide = data.get('sulphide')

            # Log the extracted values
            print(f"MAC Address: {mac_address}")
            print(f"CO: {co}, NOx: {no2}, CO2: {co2}, Sulphide: {sulphide}")

            # Check if all required data is present
            if all([mac_address, co, no2, co2, sulphide]):
                # Retrieve the IOTMAP instance based on the MAC address
                try:
                    iot_map_instance = IOT.objects.get(iot_id=mac_address)
                except IOT.DoesNotExist:
                    return JsonResponse({"status": "error", "message": "IOT device not found"}, status=404)

                # Create a new SensorData entry
                sensor_data = SensorData(
                    iot_id=iot_map_instance,
                    co=co,
                    nox=no2,
                    co2=co2,
                    so2=sulphide
                )
                sensor_data.save()  # Save the new sensor data to the database

                return JsonResponse({"status": "success", "message": "Data received and saved!", "mac": mac_address})

            else:
                return JsonResponse({"status": "error", "message": "Missing data fields"}, status=400)

        except json.JSONDecodeError:
            print("Invalid JSON received")  # Log error
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)




from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Challan

def payment_success(request):
    challan_id = request.GET.get('challan_id')
    challan = get_object_or_404(Challan, id=challan_id)

    # ✅ Mark Challan as Paid
    challan.paid = True
    challan.save()

    return JsonResponse({
        'status': 'success',
        'message': f'Payment received for Challan {challan_id}'
    })

def payment_cancel(request):
    return JsonResponse({
        'status': 'failed',
        'message': 'Payment cancelled by the user'
    })
