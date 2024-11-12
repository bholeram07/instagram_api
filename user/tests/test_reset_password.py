from rest_framework.exceptions import ValidationError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.test import APITestCase
from rest_framework import status
from user.serializers import ResetPasswordSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from user.models import User

class ResetPasswordTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword123",
            username="abcd"
        )
        self.token = PasswordResetTokenGenerator().make_token(self.user)
        self.user_id = urlsafe_base64_encode(str(self.user.id).encode())

    def test_reset_password_success(self):
        data = {
            "new_password": "Bhole057p@",
            "confirm_password": "Bhole057p@"
        }
        context = {
            "user_id": self.user_id,
            "token": self.token
        }
        serializer = ResetPasswordSerializer(data=data, context=context)
        self.assertTrue(serializer.is_valid())
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Bhole057p@"))

    def test_reset_password_password_mismatch(self):
        data = {
            "new_password": "newpassword123",
            "confirm_password": "differentpassword123"
        }

        context = {
            "user_id": self.user_id,
            "token": self.token
        }

        serializer = ResetPasswordSerializer(data=data, context=context)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password does not match with the confirm password", str(serializer.errors))

    def test_reset_password_invalid_token(self):
        invalid_token = "invalidtoken"

        data = {
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }

        context = {
            "user_id": self.user_id,
            "token": invalid_token
        }

        serializer = ResetPasswordSerializer(data=data, context=context)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
