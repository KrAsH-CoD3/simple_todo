from rest_framework import serializers
from .models import BotTask

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotTask
        fields: list[str] = ['id', 'title', 'data']
        read_only_fields: list[str] = ['id']