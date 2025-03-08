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

#@csrf_exempt

@api_view(['POST'])
def checkStatus(self,request):
        
        data=json.loads(request)
        mac_address = data.get('mac_address')
        iot_device = IOT.objects.filter(iot=mac_address).first()

        if not iot_device:
            return Response({"response": "IOT_id_not_exist"}, status=status.HTTP_200_OK)

        else:

            no_plate=IOT.objects.get(iot=mac_address)
            # Calculate the next data collection date
            last_data = PollutionEstimate.objects.filter(iot=mac_address).order_by('-timestamp').first()

            if last_data:
                next_due_date = last_data.timestamp + timedelta(days=180)
            else:
                next_due_date = Vehicle.objects.get(number_plate=no_plate).year  # Use initial assigned date if no data exists

            current_date = timezone.now().date()

            if current_date >= next_due_date:
                    return Response({"status": "registered", "action": "yes"}, status=status.HTTP_200_OK)
            else:
                    return Response({"status": "registered", "action": "no"}, status=status.HTTP_200_OK)   

            vehicle = Vehicle.objects.get(iot_id=mac_address)
            return Response({"status": "registered", "registration_date": vehicle.year}, status=status.HTTP_200_OK)
            

        


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




from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CustomUser, Vehicle, IOT
from django.contrib import messages

# Role Checks
def is_data_input(user):
    return user.role == 'dataInput'

def is_admin(user):
    return user.role == 'admin'

# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"status": "success"})
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')

# Dashboard
#@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


# User Registration (Only for dataInput role)
#@login_required
def register_user(request):
    if request.method == "POST":
        owner_name = request.POST['owner_name']
        owner_uid=request.POST['owner_uid']
        number_plate = request.POST['number_plate']
        year = request.POST['year']
        iot_id = request.POST['iot_id']

        print(owner_name)
        print(owner_uid)
        print(number_plate)
        print(year)
        # Create Vehicle
        vehicle = Vehicle.objects.create(number_plate=number_plate, year=year,owner=owner_name)

        # Create IoT
        iot = IOT.objects.create(iot=iot_id, number_plate=vehicle, owner=owner_name)

        messages.success(request, "User registered successfully!")
        return redirect(reverse('register_user'))

    return render(request, 'register_user.html')

# Logout
def logout_view(request):
    logout(request)
    return JsonResponse({"status": "success", "message": "Logged out successfully"})



def register(request):
    return render(request,'register_user.html')