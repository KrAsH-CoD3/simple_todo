import email
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from django.db import transaction
from uuid import uuid4

# from rest_framework.generics import ListAPIView

from .models import OneTimePassword, Subscription, CustomUser # SAME AS BELOW
# from accounts.models import OneTimePassword, Subscription
from todoapp import serializers
from .serializers import (
    UserRegisterSerializer, 
    UserLoginSerializer, 
    UserPasswordResetSerializer,
    UserSetNewPasswordSerializer,
    SubscriptionSerializer,
    CloudinaryUploadSerializer,

    cloudinary # Cloud image Service API(since it has already been imported in the serializers.py file)
)
from django.contrib.auth import get_user_model
from .utils import send_code_to_user
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from json import loads as json_loads, JSONDecodeError
import hmac, hashlib, requests


User = get_user_model() # Get the current active user model(CustomUser)


class UserRegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request) -> Response:
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save() # Returns the user class (CustomUser in this case)

                send_code_to_user(serializer.data['email'])

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error Occured: {e}")
            return Response({"error": "Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class UserinitiateSubscriptionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        amount = 5000  # Example: 5000 Naira
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "email": user.email,
            "amount": amount * 100,  # Convert to kobo (paystack) format
            "reference": f"SUB-{user.id}-{uuid4().hex}",
        }

        try:
            response = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                subscription = self.create_or_update_subscription(
                    user, 
                    "premium", 
                    amount, 
                    data['reference']
                )
                if subscription:
                    return Response(response_data, status=status.HTTP_200_OK)
            return Response({"error": "Payment initialization failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error Occured: {e}")
            return Response({"error": "Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_or_update_subscription(self, user, plan, amount, reference):
        """
        Create or update a subscription for a user and plan.
        """
        try:
            with transaction.atomic():
                # subscription = Subscription.objects.filter(
                #     user=user,
                #     plan=plan,
                #     status__in=['expired', 'pending']  # Look for existing records
                # ).first()

                if subscription:= Subscription.objects.filter(
                    user=user,
                    plan=plan,
                    status__in=['expired', 'pending', 'active']
                ).first():
                    if subscription.status in ['expired', 'pending']:
                        # Update the existing subscription with the newly intiated subscription
                        # if it status is expired or pending
                        subscription.status = 'pending'
                        subscription.amount_paid = amount
                        subscription.reference = reference
                        subscription.save()
                    elif subscription.status == 'active': ...
                        # DO something here if we have different subscription plans

                        # # Create a new subscription if the current one is active
                        # subscription = Subscription.objects.create(
                        #     user=user,
                        #     plan=plan,
                        #     status='pending',
                        #     amount_paid=amount,
                        #     reference=reference  # New reference
                        # )
                else:
                    # If no subscription found, create a new one
                    subscription = Subscription.objects.create(
                        user=user,
                        plan=plan,
                        status='pending',
                        amount_paid=amount,
                        reference=reference
                    )
            return subscription
        except Exception as e:
            print(f"Error creating/updating subscription: {str(e)}")
            return None


class UserVerifySubscriptionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reference = request.data.get('reference')
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }
        response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
        print(response.json())
        print(response.status_code)

        if response.status_code == 200:
            response_data = response.json()
            if response_data['data']['status'] == 'success':
                # Subscription.objects.create(
                #     user=request.user,
                #     plan='premium',
                #     status='active',
                #     amount_paid=response_data['data']['amount'],
                #     reference=response_data['data']['reference']
                # )
                return Response({"message": "Payment verified successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)


class WebhookVerifySubscriptionView(generics.GenericAPIView):
    ALLOWED_IPS = settings.PAYSTACK_IPS

    def dispatch(self, request, *args, **kwargs):
        """
        Overridden dispatch method to check if the client's IP address is allowed before processing the request.

        Checks if the client's IP address is present in the `ALLOWED_IPS` list. If not, returns a 403 Forbidden response.
        Otherwise, proceeds with the request by calling the superclass's dispatch method.
        """
        ip_address = self.get_client_ip(request)
        
        if ip_address not in self.ALLOWED_IPS:
            return Response({'error': 'Unauthorized IP'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().dispatch(request, *args, **kwargs)

    def get_client_ip(self, request):
        """
        Extracts the client's IP address from the request headers.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0] # IP Address
        else:
            return request.META.get('REMOTE_ADDR') # IP Address

    def post(self, request):
        secret_key = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
        paystack_signature = request.headers.get('X-Paystack-Signature')
        if not paystack_signature:
            return Response({'error': 'Missing Paystack signature'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = json_loads(request.body)
            print(f"{payload.get('event', payload) = }")
            event_type = payload.get('event')
            
            if event_type == "charge.success":
                return self.handle_charge_success(payload, secret_key, paystack_signature)
            elif event_type == "subscription.create":
                return self.handle_subscription_create(payload)
            else:
                return Response({'status': 'Unhandled Event'}, status=status.HTTP_200_OK)
        except JSONDecodeError as e:
            # If the payload is not JSON
            print(f"JSONDecodeError Occured: {e}") # LOG THIS
            return Response({'error': 'Invalid JSON payload'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Catch other exceptions
            print(f"Error Occured: {e}") # LOG THIS
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

    def handle_charge_success(self, payload, secret_key, paystack_signature) -> Response:
        """
        Handle successful charge events.
        """
        data = payload.get('data', {})

        reference = data.get('reference')
        print(f"{data.get('reference') = }")
        # amount = data.get('amount')
        # customer_email = data.get('customer', {}).get('email')
        # print(f"Payment received: {reference} - {amount} from {customer_email}") # TODO: LOG THIS
        
        computed_signature = hmac.new(
            key=secret_key,
            msg=self.request.body, # Accepts bytes and Request body is in bytes by default
            digestmod=hashlib.sha512
        ).hexdigest()

        if computed_signature != paystack_signature:
            return Response({'error': 'Invalid Paystack signature'}, status=status.HTTP_400_BAD_REQUEST)

        if subscription:= Subscription.objects.filter(reference=reference).first():
            subscription.status = 'active'
            subscription.start_date = now()
            subscription.end_date = now() + timedelta(days=30)
            subscription.amount_paid = data['amount'] / 100
            subscription.save()
            return Response({"message": "Subscription updated successfully"}, status=status.HTTP_200_OK)

        print("Your ass is an Hacker!!!")
        # Do something else if subscription doesn't exist(likely an hacker)
        return Response({'status': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

    def handle_subscription_create(self, payload):
        """
        Handle subscription creation events.
        """
        print(f"Subscription created: {payload}")
        # Add logic to process subscription creation

      
class UserSubscriptionListView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get(self, request):
        subscriptions = Subscription.objects.filter(user=request.user).order_by('-start_date')
        # print(subscriptions)
        if subscriptions.exists():
            subs_data = [
                SubscriptionSerializer(subscription).data for subscription in subscriptions
            ]
            return Response({"status": "ok", "subscriptions": subs_data})
        return Response({"Status": "ok", "subscriptions": []})


class ActiveSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscription = Subscription.objects.filter(user=request.user, status='active').first()
        if not subscription:
            return Response({"error": "No active subscription found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ProfilePictureUpdateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        new_image = request.FILES.get('profile_picture_image')
        if not new_image:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.filter(email=request.user.email).first()
        if user:
            current_image_url = user.profile_image_url
            
            try:
                # Extract the Cloudinary public_id from the URL (if exists)
                if current_image_url:
                    public_id = current_image_url.split('/')[-1].split('.')[0] # Image name without extension

                    # Delete the existing image from Cloudinary
                    cloudinary.uploader.destroy(public_id)

                upload_data = cloudinary.uploader.upload(new_image) 
                cloudinary_url: str | None = upload_data.get('secure_url')
                user.profile_image_url = cloudinary_url
                user.save()
                
                return Response({"url": cloudinary_url}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "No user found"}, status=status.HTTP_400_BAD_REQUEST)
