# from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models.manager import BaseManager
from rest_framework.response import Response
from rest_framework.request import Request
from .serializers import TaskSerializer
from rest_framework import status
from .models import Task


@api_view(['GET'])
def index(request: Request) -> Response:
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
# @permission_classes([IsAuthenticated])
def task_list(request: Request) -> Response:
    tasks: BaseManager[Task] = Task.objects.all().filter(user=request.user).order_by('-id') # Queryset
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail(request: Request, pk) -> Response:
    try:
        task: Task = Task.objects.get(pk=pk, user=request.user) # Only fetch task if it belongs to the user
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def task_create(request: Request) -> Response:
    task = TaskSerializer(data=request.data)
    if not task.is_valid():
        return Response(task.errors, status=status.HTTP_400_BAD_REQUEST)
    task.save(user=request.user)
    return Response(task.data, status=status.HTTP_201_CREATED)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def task_update(request: Request, pk) -> Response:
    try:
        task: Task = Task.objects.get(pk=pk, user=request.user) # Only fetch task if it belongs to the user
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serialized_task = TaskSerializer(instance=task, data=request.data)
    if not serialized_task.is_valid():
        return Response(serialized_task.errors, status=status.HTTP_400_BAD_REQUEST)
    serialized_task.save(user=request.user)
    return Response(serialized_task.data) # status=status.HTTP_200_OK

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def task_delete(request: Request, pk) -> Response:
    try:
        task: Task = Task.objects.get(pk=pk, user=request.user) # Only fetch task if it belongs to the user
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    task.delete()
    return Response({
        'status': status.HTTP_204_NO_CONTENT,
        'message': 'Task deleted successfully ✅', 
        'deleted task': {
            'title': task.title,
            'completed': task.completed,
        }
    })

