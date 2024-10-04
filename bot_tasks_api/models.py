from django.db import models

class BotTask(models.Model):
    title = models.CharField(max_length=50)
    data = models.JSONField()

    def __str__(self) -> str:
        return str(self.title)
