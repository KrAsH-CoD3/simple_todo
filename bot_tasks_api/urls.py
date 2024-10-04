from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns: list[URLPattern] = [ 
    path('save-tasks/', views.save_bot_tasks, name='save-bot-tasks'),
    path('get-tasks/<str:title>/', views.get_bot_tasks, name='get-bot-tasks'),
    path('tasks/', views.get_all_bot_tasks, name='get-bot-tasks'),
]