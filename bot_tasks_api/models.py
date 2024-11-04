from django.db import models

class BotTask(models.Model):
    # verbose_name as a parameter in the field definition is the name that will appear in the form(django admin as an example)
    owner = models.CharField(max_length=50, verbose_name="Owner(API Key)") 
    title = models.CharField(max_length=50, unique=True, verbose_name="Task Title")
    data = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
    execution_count = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.title)
    
    class Meta: # This is for the admin dashboard
        verbose_name: str = "Bot Task 😁" # How it be would be displayed when creating new task from the admin dashboard
        verbose_name_plural: str = "Bot Tasks 😈" # How it be would be displayed in the admin dashboard at the side(if you wanna view all bot tasks)