from django.core.mail import send_mail
import os
from random import randint


def generate_otp():
    otp = str(randint(000000, 999999))
    return otp


def send_test_mail(data):
    send_mail(
        subject=data["subject"],
        message=data["body"],
        from_email=os.environ.get("EMAIL_FROM"),
        recipient_list=[data["to_email"]],
    )


def format_errors(errors):
    """
    Customize the error message to return a separate line for each error.
    This function returns a list of errors instead of a single string.
    """
    error_messages = []

    # Loop through each error field and format the message
    for field, messages in errors.items():
        for message in messages:
            # Add each error message to the list with the field name
            error_messages.append(f"{field}: {message}")

    # Return the list of error messages (not a single string with '\n')
    return error_messages