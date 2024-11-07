from django.core.mail import send_mail
import os
from random import randint


def generate_otp():
    otp = str(randint(000000,999999))
    return otp


def send_test_mail(data):
    send_mail(
        subject=data["subject"],
        message=data["body"],
        from_email=os.environ.get("EMAIL_FROM"),
        recipient_list=[data["to_email"]],
    )
