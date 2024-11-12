from django.contrib import admin
from django.urls import path, include
from django.urls.resolvers import URLResolver

urlpatterns: list[URLResolver] = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls')),
    path('api/', include('todoapp.urls')),
    path('bot/', include('bot_tasks_api.urls')),
    path('accounts/', include('accounts.urls')),
]

