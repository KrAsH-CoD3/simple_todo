from django.db import models
# from rest_framework.serializers import ValidationError

class BotTask(models.Model):
    owner = models.CharField(max_length=50)
    title = models.CharField(max_length=50, unique=True)
    data = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
    execution_count = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.title)
    
    # def validate_title(self, value):
    #     """
    #     Check that the title is not already in the database.
    #     """
    #     if BotTask.objects.filter(title=value).exists():
    #         raise ValidationError('Title already exists')
    #     return value