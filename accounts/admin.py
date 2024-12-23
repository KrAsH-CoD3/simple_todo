from django.contrib import admin
from .models import CustomUser, OneTimePassword, Subscription

# Register your models here.
admin.site.register([CustomUser, OneTimePassword, Subscription])