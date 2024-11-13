from django.urls import reverse
from user.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase


class LogoutTestCase(TestCase):
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
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_logout(self):
        """Test logout functionality"""
        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("update-password"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
