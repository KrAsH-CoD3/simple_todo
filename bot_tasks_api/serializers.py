from rest_framework import serializers
from .models import BotTask

class TaskSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = BotTask
        fields: list[str] = ['id', 'owner', 'title', 'data', 'created', 'execution_count']
        read_only_fields: list[str] = ['id']