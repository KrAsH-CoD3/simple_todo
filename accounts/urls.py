from django.urls import include, path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('verify/', views.VerifyUserEmailView.as_view(), name='verify'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('test-login/', views.TestUserLoginView.as_view(), name='test_login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('refresh/', views.UserRefreshView.as_view(), name='refresh'),

    # JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]