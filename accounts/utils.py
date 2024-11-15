import random
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import OneTimePassword

User = get_user_model()

generateOTP = lambda: ''.join(random.choices('123456789', k=6))

def send_code_to_user(email):   
    subject = "Email Verification Code"
    otp_code = generateOTP()
    user = User.objects.get(email=email)
    # THIS PART IS INDENTED CUS OF HOW IT WOULD BE DISPLAYED IN THE MAIL
    email_body = f'''Hello {user.first_name.capitalize()},
Welcome to Simple Todo App.
Your account was created successfully.
Your OTP Code is `{otp_code}`.'''
    from_email = settings.DEFAULT_FROM_EMAIL

    OneTimePassword.objects.create(user=user, otp_code=otp_code) # Create OTP associated to the user

    email_to_send = EmailMessage(
        subject=subject,
        body=email_body,
        from_email=from_email, 
        to=[email]
    )
    # email_to_send.send(fail_silently=False)
    print("OTP Code: " + otp_code)
