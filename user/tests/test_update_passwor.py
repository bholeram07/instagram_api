from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user.models import User


class UpdatePasswordTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="Bhole057p@", email="abc@gmail.com"
        )
        self.user.is_verified = True
        self.user.save()
        self.client = APIClient()
        response = self.client.post(
            reverse("login"), {"email": "abc@gmail.com", "password": "Bhole057p@"}
        )
        self.access_token = response.data.get("access")
        if not self.access_token:
            self.fail(
                "Login did not return a token. Check if 'IsUserVerified' permission blocks unverified users."
            )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

    def test_update_password(self):
        response = self.client.put(
            reverse("update-password"),
            {
                "email": "abc@gmail.com",
                "current_password": "Bhole057p@",
                "new_password": "Bhole057p@1",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.client.credentials()
        login_response = self.client.post(
            reverse("login"), {"email": "abc@gmail.com", "password": "Bhole057p@1"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)
