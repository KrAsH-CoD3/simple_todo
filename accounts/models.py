# from time import timezone
from django.db import models as db_models
from django.contrib.auth import models as auth_models
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q


class CustomUserManager(auth_models.BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email) # Making sure it follow RFC email format
        except ValidationError:
            raise ValueError(_('Please enter a valid email address!'))

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('User must have an email address'))
        
        email = self.normalize_email(email) # Setting email to lowercase(domain part)
        self.email_validator(email)
        
        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(
            email=email,
            password=password,
            **extra_fields
        )


class CustomUser(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    # Since null and blank are not defined in the email field and email is used as username so it is definitely required
    email = db_models.EmailField(unique=True, max_length=50, verbose_name=_('Email address'))

    # These fields are REQUIRED since both null and blank are False
    first_name = db_models.CharField(max_length=30, null=False, blank=False, verbose_name=_("First Name")) 
    username = db_models.CharField(max_length=30, null=False, blank=False, verbose_name=_("Username"))

    # null is false if not defined in the field
    # (meaning that field must be passed when creating/updating a user if no default value is provided)
    # Optional field since we have default value. NOTE: this is for DB level
    # If last_name is not passed in serializer, it will raise error since it is required in the user model creation
    last_name = db_models.CharField(max_length=30, blank=True, default='', verbose_name=_("Last Name")) 
    subscription_status = db_models.CharField(max_length=10, default='free')  # 'free' or 'premium'
    profile_image_url = db_models.URLField(max_length=500, blank=True, null=True, verbose_name=_("Profile Image URL"))

    is_active = db_models.BooleanField(default=True)
    is_staff = db_models.BooleanField(default=False)
    is_superuser = db_models.BooleanField(default=False)
    is_verified = db_models.BooleanField(default=False)
    date_joined = db_models.DateTimeField(auto_now_add=True)
    last_login = db_models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name'] # For creating superuser using `createsuperuser` command

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def clean(self):
        if self.first_name == self.last_name:
            raise ValidationError('First name and last name cannot be the same.')
        return self


class Subscription(db_models.Model):
    PLAN_CHOICES = [
        ('free', 'Free Plan'),
        ('premium', 'Premium Plan'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ]

    user = db_models.ForeignKey(CustomUser, on_delete=db_models.CASCADE, related_name='subscriptions')
    plan = db_models.CharField(max_length=10, choices=PLAN_CHOICES) #default='free'
    status = db_models.CharField(max_length=10, choices=STATUS_CHOICES)
    amount_paid = db_models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reference = db_models.CharField(max_length=100, unique=True, blank=True, null=True)  # Paystack transaction ref
    start_date = db_models.DateTimeField(auto_now_add=True)
    end_date = db_models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

        constraints = [
            db_models.UniqueConstraint(
                fields=['user', 'plan'], 
                condition=Q(status__in=['expired', 'pending']), 
                name='unique_pending_subscription_per_user_plan'
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.plan} - {self.status}"

    # def __str__(self):
    #     return f"{self.user.username}'s subscription"
    

class OneTimePassword(db_models.Model):
    user = db_models.ForeignKey(CustomUser, on_delete=db_models.CASCADE)
    otp_code = db_models.CharField(max_length=6, verbose_name=_('OTP Code'))
    created = db_models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'One Time Password'
        verbose_name_plural = 'One Time Passwords'

    def __str__(self):
        return f"{self.user.email} OTP Code"