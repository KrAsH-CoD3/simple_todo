from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'id': 'LaughsLOUD-BOY'
        }),
        help_text="Ubudu Weei",
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('This email is already registered.'))
        return email


# class LoginForm(AuthenticationForm):
#     class Meta:
#         model = get_user_model()
#         fields = ['username', 'password']
