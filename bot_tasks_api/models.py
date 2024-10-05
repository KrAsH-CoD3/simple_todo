from django.db import models

class BotTask(models.Model):
    owner = models.CharField(max_length=50) # APIKEY
    title = models.CharField(max_length=50, unique=True)
    data = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
    execution_count = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.title)