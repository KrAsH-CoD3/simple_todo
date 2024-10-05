from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns: list[URLPattern] = [ 
    path('save-task/', views.save_bot_task, name='save-bot-task'),
    path('get-task/<str:title>/', views.get_task, name='get-task'),
    path('tasks/', views.get_all_bot_tasks, name='get-all-bot-tasks'),
    path('delete-task/<str:title>/', views.delete_bot_task, name='delete-bot-task'),
    path('update-task/<str:title>/', views.update_bot_task, name='update-bot-task'),
]