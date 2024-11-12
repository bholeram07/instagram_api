from django.test import TestCase
from django.core import mail
from user.utils import send_test_mail  

class SendMailTestCase(TestCase):
    def test_send_test_mail(self):
        email_data = {
            "subject": "Test Subject",
            "body": "This is a test email body.",
            "to_email": "test@example.com"
        }
        send_test_mail(email_data)
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, email_data["subject"])
        self.assertEqual(sent_email.body, email_data["body"])
        self.assertEqual(sent_email.to, [email_data["to_email"]])
