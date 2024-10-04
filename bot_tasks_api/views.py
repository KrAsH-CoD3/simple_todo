# from django.shortcuts import render
from django.db.models.manager import BaseManager
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TaskSerializer
from .models import BotTask

@api_view(['GET'])
def get_bot_tasks(request, title) -> Response:
    tasks: BotTask = BotTask.objects.get(title=title) 
    serializer = TaskSerializer(tasks)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_bot_tasks(request) -> Response:
    tasks: BaseManager[BotTask] = BotTask.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def save_bot_tasks(request) -> Response:
    tasks = TaskSerializer(data=request.data)
    if not tasks.is_valid():
        return Response(tasks.errors, status=400)
    tasks.save()

    return Response({
        'status': 200,
        'message': 'Tasks saved successfully ✅',
    })
