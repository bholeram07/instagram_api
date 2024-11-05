from django.core.mail import send_mail
import os


def send_test_mail(data):
    print()
    send_mail(
        subject=data["subject"],
        message=data["body"],
        from_email=os.environ.get("EMAIL_FROM"),
        recipient_list=[data["to_email"]],
    )
