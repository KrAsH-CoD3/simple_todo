# from django.shortcuts import render
from django.db.models.manager import BaseManager
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskSerializer
from .models import BotTask

@api_view(['GET'])
def get_task(request, title) -> Response:
    tasks: BotTask = BotTask.objects.get(title=title) 
    serializer = TaskSerializer(tasks)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_bot_tasks(request) -> Response:
    tasks: BaseManager[BotTask] = BotTask.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def save_bot_task(request) -> Response:
    tasks = TaskSerializer(data=request.data)
    if not tasks.is_valid():
        return Response(tasks.errors, status=status.HTTP_400_BAD_REQUEST)
    tasks.save()

    return Response({
        'status': 'success',
        'message': 'Tasks saved successfully ✅',
    }, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
def delete_bot_task(request, title) -> Response:
    tasks: BotTask = BotTask.objects.get(title=title)
    tasks.delete()

    return Response({
        'status': status.HTTP_204_NO_CONTENT,
        'message': 'Tasks deleted successfully ✅',
    }, status=status.HTTP_204_NO_CONTENT)
