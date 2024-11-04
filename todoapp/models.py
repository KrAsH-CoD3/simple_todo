from django.db import models
# from django.contrib.auth.models import User # NOT THE BEST PRACTICE
from django.contrib.auth import get_user_model # BEST PRACTICE: To get the current active user model
# from django.conf import settings


# Create your models here.
class Task(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title
    