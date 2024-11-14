from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from accounts.models import OneTimePassword
from .serializers import UserRegisterSerializer, UserLoginSerializer
from django.contrib.auth import get_user_model
from .utils import send_code_to_user

User = get_user_model() # Get the current active user model(CustomUser)


# class UserRegisterView(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = UserRegisterSerializer
#     queryset = User.objects.all()

class UserRegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs) -> Response:
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

# class UserRegisterView(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = UserRegisterSerializer
#     queryset = User.objects.all()

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         return Response(UserRegisterSerializer(user).data, status=201)


# class UserLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = User.objects.get(username=username)
#         if user.check_password(password):
#             token = user.token_for_user(RefreshToken)
#             return Response({'token': token}, status=200)
#         return Response({'message': 'Invalid username or password'}, status=401)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print(request.data)
            token = request.data.get('refresh', None)
            if not token: # Does not exist in request
                return Response({'message': 'No refresh token provided'}, status=status.HTTP_400_BAD_REQUEST)
            token =  RefreshToken(token)
            token.blacklist()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({'message': 'Invalid token or expired token.'}, status=status.HTTP_401_UNAUTHORIZED)


class UserRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        try:
            RefreshToken.objects.get(key=token)
        except RefreshToken.DoesNotExist:
            return Response({'message': 'Invalid token'}, status=401)
        user = User.objects.get(username=token.user.username)
        refreshed_token = user.token_for_user(RefreshToken)
        return Response({'token': refreshed_token}, status=200)