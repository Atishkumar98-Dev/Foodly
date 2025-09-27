from rest_framework import serializers
from .models import Food

class FoodSerializers(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'
