from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_user, name='register'),
    # path('login/', views.login_user, name='login'),
    # path('dashboard/', views.register_user, name='register'),
    # path('register/', views.register_user, name='register'),
]