# from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TaskSerializer
from .models import Task


# Create your views here.

@api_view(['GET'])
def index(request):
    return Response({
        'message': 'Welcome to the TODO APP ✅',
        'urls': {
            'List': '/task-list/',
            'Detail View': '/task-detail/<str:pk>/',
            'Create': '/task-create/',
            'Update': '/task-update/<str:pk>/',
            'Delete': '/task-delete/<str:pk>/',
        }
    })

@api_view(['GET'])
def task_list(request):
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

def task_detail(request, pk):
    task = Task.objects.get(pk=pk)
    serializer = TaskSerializer(task)
    return Response(serializer.data)

def task_create(request):
    return Response({'message': 'Hello World'})

def task_update(request, pk):
    return Response({'message': 'Hello World'})

def task_delete(request, pk):
    return Response({'message': 'Hello World'})

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