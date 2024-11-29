from rest_framework import serializers
from .models import IOT,SensorData,Vehicle

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model=SensorData
        fields = ['iot', 'co', 'nox', 'nh3', 'co2', 'benzene', 'ch4','no2','so2']
    
    def validate_co(self, value):
        if value is None:
            raise serializers.ValidationError("CO value cannot be null.")
        if value < 0:
            raise serializers.ValidationError("CO value cannot be negative.")
        return value

    def validate_no2(self, value):
        if value is None:
            raise serializers.ValidationError("NO2 value cannot be null.")
        if value < 0:
            raise serializers.ValidationError("NO2 value cannot be negative.")
        return value


    def validate_iot(self,value):
        if IOT.objects.filter(iot=value).exists():
            raise serializers.ValidationError("The specified IoT device does not exist.")
    
        return value



class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model=Vehicle
        fields=["__all__"]