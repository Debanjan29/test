from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
import json


from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

#@csrf_exempt

@csrf_exempt
def data_view(request):
    print("Request method:", request.method)  # Print request method
    print("Request body:", request.body.decode('utf-8'))  # Print request body

    if request.method == 'POST' or request.method == 'GET':
        try:
            data = json.loads(request.body)
            print("Received data:", data)
            return JsonResponse({"status": "success", "data": data})
        except json.JSONDecodeError:
            print("Invalid JSON received")  # Log error
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

ans='DebaBhat'
@api_view(['GET','POST'])
def getData(request):
    person={'name':ans,'age':16}
    return Response(person)


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

    # Print these individual values in terminal
    #print(f"MAC Address: {mac_address}, CO: {co}, NOx: {nox}, NH3: {nh3}, CO2: {co2}, Benzene: {benzene}, Sulphide: {sulphide}, CH4: {ch4}, Butane: {butane}")
    
    # Send back a success response to ESP32
    if(sensor_data):
        return JsonResponse({"status": "success", "message": "Data received!","mac":"dd"})
    else:
        return JsonResponse({"not recived":"failed"})
