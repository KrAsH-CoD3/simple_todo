# from django.shortcuts import render
from django.db.models.manager import BaseManager
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import BotTaskSerializer
from .models import BotTask

@api_view(['GET'])
def get_task(request, title) -> Response:
    tasks: BotTask = BotTask.objects.get(title=title) 
    serializer = BotTaskSerializer(tasks)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_tasks(request) -> Response:

    owner = request.GET.get('owner', None)  # Retrieve the 'owner' query parameter

    if owner:
        tasks = BotTask.objects.filter(owner__contains=owner)  # Filter Tasks by owner
    else:
        tasks: BaseManager[BotTask] = BotTask.objects.all()  # Retrieve all Tasks if no owner is provided

    serializer = BotTaskSerializer(tasks, many=True)
        
    return Response({
        "status": "success",
        "json": serializer.data,
    })

@api_view(['POST'])
def save_task(request) -> Response:
    tasks = BotTaskSerializer(data=request.data)
    if not tasks.is_valid():
        return Response(tasks.errors, status=status.HTTP_400_BAD_REQUEST)
    tasks.save()

    return Response({
        'status': 'success',
        'message': 'Tasks saved successfully ✅',
        "data": tasks.data,
    }, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
def delete_task(request, title) -> Response:
    tasks: BotTask = BotTask.objects.get(title=title)
    tasks.delete()

    return Response({
        'status': status.HTTP_204_NO_CONTENT,
        'message': 'Tasks deleted successfully ✅',
    }, status=status.HTTP_204_NO_CONTENT)

@api_view(['PATCH'])
def update_task(request, title) -> Response:
    tasks: BotTask = BotTask.objects.get(title=title)
    serializer = BotTaskSerializer(instance=tasks, data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    serializer.save()
    return Response({
        'status': status.HTTP_200_OK,
        'message': 'Task updated successfully ✅',
    }, status=status.HTTP_200_OK)