from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from accounts.models import OneTimePassword
from todoapp import serializers
from .serializers import (
    UserRegisterSerializer, 
    UserLoginSerializer, 
    UserPasswordResetSerializer,
    UserSetNewPasswordSerializer
)
from django.contrib.auth import get_user_model
from .utils import send_code_to_user

User = get_user_model() # Get the current active user model(CustomUser)


class UserRegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save() # Returns the user class (CustomUser in this case)

            send_code_to_user(serializer.data['email'])

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserEmailView(generics.GenericAPIView):
    def post(self, request):
        otp_code = request.data.get('otp_code')
        try:
            user_code_object = OneTimePassword.objects.get(otp_code=otp_code)
            user = user_code_object.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({'message': 'Successfully verified user.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'User already verified.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: # OneTimePassword.DoesNotExist
            print("Error:", e)
            return Response({'message': 'Invalid OTP Code.'}, status=status.HTTP_400_BAD_REQUEST)
        

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestUserLoginView(generics.GenericAPIView):
    serializer_class = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': 'Successfully logged in.',
        }, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = request.data.get('refresh', None)
            if not token: # Does not exist in request
                return Response({'message': 'No refresh token provided'}, status=status.HTTP_400_BAD_REQUEST)
            token =  RefreshToken(token)
            token.blacklist()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({'message': 'Invalid token or expired token.'}, status=status.HTTP_401_UNAUTHORIZED)


class UserRefreshView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        try:
            RefreshToken.objects.get(key=token)
        except RefreshToken.DoesNotExist:
            return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get(username=token.user.username)
        refreshed_token = user.token_for_user(RefreshToken)
        return Response({'token': refreshed_token}, status=status.HTTP_200_OK)


class UserResetPasswordView(generics.GenericAPIView):
    serializer_class = UserPasswordResetSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)
    

class UserConfirmPasswordResetView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except User.DoesNotExist:
                return Response({'message': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except DjangoUnicodeDecodeError:
            return Response({'message': 'Invalid UID format. Cannot decode.'}, status=status.HTTP_400_BAD_REQUEST)
    
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'message': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success' : True,
            'message': 'Credentials are valid. Continue to reset password.',
        }, status=status.HTTP_200_OK)
    

class UserSetNewPasswordView(generics.GenericAPIView):
    serializer_class = UserSetNewPasswordSerializer
    permission_classes = [AllowAny]

    def patch(self, request):
        serializers = self.get_serializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        # serializers.save()
        return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)
