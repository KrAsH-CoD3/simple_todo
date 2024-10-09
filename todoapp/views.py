# from django.shortcuts import render
from os import environ
from django.db.models.manager import BaseManager
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TaskSerializer
from .models import Task

from django.core.mail import send_mail
from dotenv import load_dotenv

load_dotenv()


# Create your views here.

@api_view(['GET'])
def index(request) -> Response:
    return Response({
        'message': 'Welcome to the TODO APP ✅',
        'urls': {
            'List': '/task-list/',
            'Detail View': '/task-detail/<int:pk>/',
            'Create': '/task-create/',
            'Update': '/task-update/<int:pk>/',
            'Delete': '/task-delete/<int:pk>/',
        }
    })

@api_view(['GET'])
def task_list(request) -> Response:
    tasks: BaseManager[Task] = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def task_detail(request, pk) -> Response:
    task: Task = Task.objects.get(pk=pk)
    serializer = TaskSerializer(task)
    return Response(serializer.data)

@api_view(['POST'])
def task_create(request) -> Response:
    task = TaskSerializer(data=request.data)
    if not task.is_valid():
        return Response(task.errors, status=400)
    task.save()
    send_mail(
        "Task created successfully",
        f"Welcome to our API.\nYou have successfully created the task \"{request.data['title']}\". 🎉",
        environ['EMAIL_HOST_USER'],
        [request.data['email']],
        fail_silently=True,
    )
    return Response(task.data, status=201)

@api_view(['PATCH'])
def task_update(request, pk) -> Response:
    task: Task = Task.objects.get(pk=pk)
    serializer = TaskSerializer(instance=task, data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def task_delete(request, pk) -> Response:
    task: Task = Task.objects.get(pk=pk)
    task.delete()
    return Response({
        'status': 200,
        'message': 'Task deleted successfully ✅', 
        'task': {
            'title': task.title,
            'completed': task.completed,
        }
    })