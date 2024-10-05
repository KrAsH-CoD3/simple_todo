from django.db import models
from django.utils import timezone

class BotTask(models.Model):
    owner = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    data = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
    execution_count = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.title)
