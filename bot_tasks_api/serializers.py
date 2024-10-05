from rest_framework import serializers
from .models import BotTask

class BotTaskSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)  # Ensure it's marked as read-only

    class Meta:
        model = BotTask
        fields: list[str] = ['id', 'owner', 'title', 'data', 'created', 'execution_count']
        # read_only_fields: list[str] = ['id', 'created', 'execution_count']