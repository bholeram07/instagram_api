from django.test import TestCase
from user.models import User
from user.models import OtpVerification
from user.serializers import VerifyOtpSerializer
from rest_framework.exceptions import ValidationError


class VerifyEmailTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )
        self.otp = "123456"
        self.otp_record = OtpVerification.objects.create(user=self.user, otp=self.otp)

    def test_verify_email_success(self):
        data = {"email": self.user.email, "otp": self.otp}

        serializer = VerifyOtpSerializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            self.user.refresh_from_db()
            self.assertTrue(self.user.is_verified)
        except ValidationError as e:
            self.fail(f"Validation failed: {e}")

    def test_invalid_otp(self):
        data = {"email": self.user.email, "otp": "000000"}  # Invalid OTP

        serializer = VerifyOtpSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_expired_otp(self):
        self.otp_record.delete()
        data = {"email": self.user.email, "otp": self.otp}

        serializer = VerifyOtpSerializer(data=data)

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_already_verified_user(self):
        self.user.is_verified = True
        self.user.save()

        data = {"email": self.user.email, "otp": self.otp}
        serializer = VerifyOtpSerializer(data=data)

        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)

        self.assertIn("User Already verified", cm.exception.detail["non_field_errors"])
