from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User # Used `get_user_model` instead
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            # 'class': 'form-control',
            'placeholder': 'Enter your email',
            'id': 'Tag_id_would_be_here'
        }),
        help_text="Use gmail to get registration mail.",
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            # 'class': 'form-control',
            'placeholder': 'First name',
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            # 'class': 'form-control',
            'placeholder': 'Last name',
            'autofocus': '' # Making sure the lastname field is focused. autofocus is usually on the username field by default.
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


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username', 
        max_length=30, 
        widget=forms.TextInput(attrs={'class': 'user_class_value'})
    )
    password = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput(attrs={'class': 'password_class_value'})
    )

    # NOT NECESSARY UNLESS YOU WANNA MAYBE UPDATE THE ATTRIBUTES OR SOMETHING
    # def __init__(self, *args, **kwargs):
    #     super(LoginForm, self).__init__(*args, **kwargs)
    #     self.fields['username'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['password'].widget.attrs.update({'class': 'form-control'})

    # Incase you wanna do some other validation
    # def clean(self):
    #     # Call super() to retain the default clean behavior of AuthenticationForm
    #     cleaned_data = super().clean()
    #     username: Any | None = cleaned_data.get('username')
    #     password: Any | None = cleaned_data.get('password')

    #     # DO SOMETHING WITH THE FIELD VALUES(in this case username and password)
    #     # REMEMBER NOT TO AUTHENTICATE AGAIN AS IT HAS ALREADY BEEN DONE IN THE SUPER CLEAN METHOD

    #     return cleaned_data

    # Individual field validation
    # def clean_email(self):
        # DO SOMETHING WITH THE FIELD VALUE
        # return cleaned_data
