from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Create your views here.

@api_view(['GET'])
def index(request):
    return Response({'message': 'Welcome to the homepage ✅'})

@api_view(['POST'])
def add(request):
    return Response({'message': 'Hello World'})

@api_view(['GET'])
def delete(request, id):
    return Response({'message': 'Hello World'})

@api_view(['GET'])
def update(request, id):
    return Response({'message': 'Hello World'})

@api_view(['GET'])
def complete(request, id):
    return Response({'message': 'Hello World'})