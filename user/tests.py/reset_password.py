import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse


@pytest.mark.django_db
class TestResetPassword:
    def setup_method(self):
        self.user = get_user_model().objects.create_user(
           username = "bholerampatidar", email="testuser@example.com", password="old_password123"
        )
        self.client = APIClient()
        self.client.login(email="testuser@example.com", password="old_password123")

    def test_reset_password_success(self):
        url = reverse("reset-password", kwargs={"user_id": self.user.id, "token": "sample_token"})
        data = {
            "current_password": "old_password123",
            "new_password": "new_password123",
            "confirm_password": "new_password123",
        }
        response = self.client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Password updated successfully"

    def test_reset_password_invalid_current_password(self):
        url = reverse("reset-password", kwargs={"user_id": self.user.id, "token": "sample_token"})
        data = {
            "current_password": "wrong_password",
            "new_password": "new_password123",
            "confirm_password": "new_password123",
        }
        response = self.client.put(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "current_password" in response.data

    def test_reset_password_new_password_mismatch(self):
        url = reverse("reset-password", kwargs={"user_id": self.user.id, "token": "sample_token"})
        data = {
            "current_password": "old_password123",
            "new_password": "new_password123",
            "confirm_new_password": "mismatched_password123",
        }
        response = self.client.put(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "confirm_new_password" in response.data

    def test_reset_password_missing_field(self):
        url = reverse("reset-password", kwargs={"user_id": self.user.id, "token": "sample_token"})
        data = {
            "new_password": "new_password123",
            "confirm_new_password": "new_password123",
        }
        response = self.client.put(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "current_password" in response.data

    def test_reset_password_unauthenticated(self):
        unauthenticated_client = APIClient()
        url = reverse("reset-password", kwargs={"user_id": self.user.id, "token": "sample_token"})
        data = {
            "current_password": "old_password123",
            "new_password": "new_password123",
            "confirm_new_password": "new_password123",
        }
        response = unauthenticated_client.put(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Authentication credentials were not provided."
