from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from food_app.models import Food
from .serializers import FoodSerializer
from rest_framework import status


# Create your views here.
@api_view(['GET', 'POST'])
def api_foodlist(request):
    if request.method == 'GET':
        foods = Food.objects.all()
        serializer = FoodSerializer(foods, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = FoodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()   # uses model’s .create()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
def api_food_detail(request, pk):
    try:
        food = Food.objects.get(id=pk)
    except Food.DoesNotExist:
        return Response({"error": "Food not found"}, status=404)

    serializer = FoodSerializer(food)
    return Response(serializer.data)