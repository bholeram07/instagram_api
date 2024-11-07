from celery import shared_task
from .utils import send_test_mail
from django.contrib.auth import get_user_model


@shared_task
def send_email(user_id, message, subject=""):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    email_data = {
        "subject": subject,
        "body": message,
        "to_email": user.email,
    }
    send_test_mail(email_data)
