
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def send_welcome_email(user_id):
    try:
        user = User.objects.get(id=user_id)
        subject = "Welcome to Our App!"
        html_message = render_to_string('welcome_email.html', {
            'user_name': user.username,
            'year': 2024
        })
        
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email

    
        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
    
    except User.DoesNotExist:
        print("User does not exist.")

@shared_task
def send_otp_email(user_id, otp_code):
    try:
         user = User.objects.get(id = user_id)
         subject = 'Your OTP Verification Code'
         html_message = render_to_string('send_otp.html', {
        'user_name': user.username,
        'otp_code': otp_code,
        })
         plain_message = strip_tags(html_message)
         from_email = settings.DEFAULT_FROM_EMAIL
         to_email = user.email

         send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
        
    except User.DoesNotExist:
        print("User does not exist")

@shared_task
def send_reset_password_email(user_id, reset_link):
    user = User.objects.get(id = user_id)
    subject = "Password Reset Request"
    html_message = render_to_string(
        "password_reset_email.html", {"user": user, "reset_link": reset_link}
    )
    plain_message = strip_tags(html_message)
    from_email = "no-reply@yourwebsite.com"
    
    send_mail(
        subject,
        plain_message,
        from_email,
        [user.email],
        html_message=html_message,
    )