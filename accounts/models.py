# from time import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email) # Making sure it follow RFC email format
        except ValidationError:
            raise ValueError(_('Please enter a valid email address!'))

    def create_user(self, email, first_name, last_name, username, password1, password2, **extra_fields):
        if not email:
            raise ValueError(_('User must have an email address'))

        if password1 != password2: # This is done in the serializer(Remember DRY)
            raise ValidationError(_('Passwords do not match!'))
        
        email = self.normalize_email(email) # Setting email to lowercase(domain part)
        self.email_validator(email)
        
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            username=username,
            **extra_fields
        )

        user.set_password(password1)
        user.full_clean()
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, username, password1, password2, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(
            email=email, 
            first_name=first_name, 
            last_name=last_name, 
            username=username, 
            password1=password1, 
            password2=password2, 
            **extra_fields
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Since null and blank are not defined in the email field and email is used as username so it is definitely required
    email = models.EmailField(unique=True, max_length=50, verbose_name='Email address')

    # These fields are REQUIRED since both null and blank are False
    first_name = models.CharField(max_length=30, null=False, blank=False, verbose_name=_("First Name")) 
    username = models.CharField(max_length=30, null=False, blank=False, verbose_name=_("Username"))

    # null is false if not defined in the field
    # (meaning that field must be passed when creating/updating a user if no default value is provided)
    # Optional field since we have default value. NOTE: this is for DB level
    # If last_name is not passed in serializer, it will raise error since it is required in the user model creation
    last_name = models.CharField(max_length=30, blank=True, default='', verbose_name=_("Last Name")) 

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username'] # For creating superuser using `createsuperuser` command

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def clean(self):
        if self.first_name == self.last_name:
            raise ValidationError('First name and last name cannot be the same.')
        return self