
from django.core.mail import EmailMessage
from django.conf import settings
import os


class Util:
    @staticmethod
    def send_mail(data):
        email= EmailMessage(
            subject = data['subject'],
            body = data['body'],
            from_email = os.environ.get('EMAIL_FROM'),
            # to=[os.environ.get('EMAIL_TO')]  
             )
        email.send()