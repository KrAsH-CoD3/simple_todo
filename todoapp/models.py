from django.db import models
from django.contrib.auth.models import User
# from django.conf import settings


# Create your models here.
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    # email = models.EmailField(max_length=200, blank=True, null=True, default=None)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    