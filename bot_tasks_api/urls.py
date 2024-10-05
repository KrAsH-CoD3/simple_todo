from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns: list[URLPattern] = [ 
    path('save-task/', views.save_task, name='save-task'),
    path('get-task/<str:title>/', views.get_task, name='get-task'),
    path('tasks/', views.get_all_tasks, name='get-all-bot-tasks'),
    path('delete-task/<str:title>/', views.delete_task, name='delete-task'),
    path('update-task/<str:title>/', views.update_task, name='update-task'),
]