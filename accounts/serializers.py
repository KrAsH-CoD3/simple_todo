from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
# from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model() # Get the current active user model(CustomUser)

class UserRegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(min_length=6, max_length=30, write_only=True)
    password2 = serializers.CharField(min_length=6, max_length=30, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'username', 'password1', 'password2']
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
            raise serializers.ValidationError('Passwords do not match!')
        
        # first_name = data.get('first_name')
        # last_name = data.get('last_name')
        # if first_name == last_name:
        #     raise serializers.ValidationError('First name and last name cannot be the same')
        return data
    
    def validate_password1(self, data):
        # print(data) # data is the value of the field
        return data

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already exists!')
        if '@gmail.com' not in email:
            raise serializers.ValidationError('Admin email only!')
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
    email = serializers.EmailField(required=True, max_length=50)
    password = serializers.CharField(max_length=30, required=True, write_only=True)
    full_name = serializers.CharField(max_length=60, read_only=True)
    access_token = serializers.CharField(max_length=60, read_only=True)
    refresh_token = serializers.CharField(max_length=60, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)
        if user is None:
            raise AuthenticationFailed('Invalid email or password')
        if not user.is_verified:
            raise AuthenticationFailed('User is not verified')
        user_tokens = user.tokens()
        return {
            'email': email, 
            'full_name': user.get_full_name,
            # 'password': password,
            'access_token': user_tokens['access'],
            'refresh_token': user_tokens['refresh'],
        }