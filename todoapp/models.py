from django.db import models

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, blank=True, null=True, default=None)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    