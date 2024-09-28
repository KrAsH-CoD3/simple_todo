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

@api_view(['GET'])
def task_detail(request, pk):
    task = Task.objects.get(pk=pk)
    serializer = TaskSerializer(task)
    return Response(serializer.data)

@api_view(['POST'])
def task_create(request):
    task = TaskSerializer(data=request.data)
    if not task.is_valid():
        return Response(task.errors, status=400)
    task.save()
    return Response(task.data, status=201)

@api_view(['PATCH'])
def task_update(request, pk):
    task = Task.objects.get(pk=pk)
    serializer = TaskSerializer(instance=task, data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def task_delete(request, pk):
    task = Task.objects.get(pk=pk)
    task.delete()
    return Response({
        'status': 200,
        'message': 'Task deleted successfully ✅', 
        'task': {
            'title': task.title,
            'completed': task.completed,
        }
    })
