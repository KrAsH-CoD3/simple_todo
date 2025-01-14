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
    path('password-reset/', views.UserResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', views.UserConfirmPasswordResetView.as_view(), name='password_reset_confirm'),
    path('set-new-password/', views.UserSetNewPasswordView.as_view(), name='set_new_password'),

    # JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('subscription/', views.UserinitiateSubscriptionView.as_view(), name='subscription'),
    path('subscription/verify/', views.UserVerifySubscriptionView.as_view(), name='verify_subscription'),
    path('subscription/list/', views.UserSubscriptionListView.as_view(), name='list_subscription'),
    path('subscription/active/', views.ActiveSubscriptionView.as_view(), name="active_subscription"),
    path('webhook/paystack/', views.WebhookVerifySubscriptionView.as_view(), name='paystack_webhook'),
    path('profile-picture-update/', views.ProfilePictureUpdateView.as_view(), name='profile_picture_update'),
]