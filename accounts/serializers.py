from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework.validators import UniqueValidator
# from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, smart_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from .utils import send_reset_password_email

User = get_user_model() # Get the current active user model(CustomUser)

class UserRegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(min_length=6, max_length=30, write_only=True)
    password2 = serializers.CharField(min_length=6, max_length=30, write_only=True)
    access_token = serializers.CharField(max_length=60, read_only=True)
    refresh_token = serializers.CharField(max_length=60, read_only=True)


    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'username', 'password1', 'password2', 'access_token', 'refresh_token']
        extra_kwargs = { # No need for this since it has already been defined in the model fields
            'last_name': {'default': ''}, # API level default value
            'first_name': {'allow_blank': True}, # API level allow blank as long as it is provided in the request
            # 'email': {'validators': [
            #     UniqueValidator(
            #         queryset=User.objects.all(),
            #         message="This email is already in use. Please use a different email address."
            #     )]}
        }

    def validate(self, data):
        password1 = data.get('password1')
        password2 = data.get('password2')
        if password1 != password2:
            raise serializers.ValidationError(_('Passwords do not match!'))
        return data
    
    def validate_password1(self, data):
        # print(data) # data is the value of the field
        return data

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(_('Email already exists!'))
        if '@gmail.com' not in email:
            raise serializers.ValidationError(_('Gmail email only allowed!'))
        return email
    
    def create(self, validated_data):
        # print(validated_data) # validated_data is the validated data in dict

        password = validated_data.pop('password1')
        validated_data.pop('password2')
        
        # return User.objects.create_user(**validated_data) # First method

        return User.objects.create_user( # Second method
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            password1=password,
            password2=password,
        )


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=50, write_only=True)
    password = serializers.CharField(max_length=30, required=True, write_only=True)
    access_token = serializers.CharField(max_length=60, read_only=True)
    refresh_token = serializers.CharField(max_length=60, read_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)
        if user is None:
            raise AuthenticationFailed(_('Invalid email or password'))
        if not user.is_verified:
            raise AuthenticationFailed(_('User is not verified'))
        user_tokens = user.tokens()
        return {
            'access_token': user_tokens['access'],
            'refresh_token': user_tokens['refresh'],
        }


class UserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=50, write_only=True)

    def validate(self, data):
        email = data.get('email')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError(_('No user with this email exists!'))
        return data
    
    def save(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id)) # Encode the user id
        token = PasswordResetTokenGenerator().make_token(user)
        request = self.context.get('request')
        site_domain = get_current_site(request).domain
        relative_link = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        absolute_link = f'http://{site_domain}{relative_link}'
        print(f'{absolute_link=}')
        send_reset_password_email(
            email, 
            'Password Reset', 
            f'Please click the link below to reset your password: {absolute_link}', 
        )
        return user # Return the user object
    

class UserSetNewPasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(min_length=6, max_length=30, write_only=True, required=True)
    password2 = serializers.CharField(min_length=6, max_length=30, write_only=True, required=True)
    uidb64 = serializers.CharField(max_length=255, write_only=True)
    token = serializers.CharField(max_length=255, write_only=True)

    # class Meta:
    #     fields = ['password1', 'password2', 'uidb64', 'token']

    def validate(self, data):
        try:
            password1 = data.get('password1')        
            password2 = data.get('password2')

            user_id = force_str(urlsafe_base64_decode(data.get('uidb64')))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, data.get('token')):
                raise AuthenticationFailed(_('Reset link is invalid or expiredd.'), code=401)
            if password1 != password2:
                raise serializers.ValidationError(_('Passwords do not match!'))
            
            user.set_password(password1)
            user.save()
            return data
        except Exception as e:
            print("An error occured:", e)
            raise AuthenticationFailed(_('Invalid reset link.'), code=401)


