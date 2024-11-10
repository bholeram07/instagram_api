import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

LOGIN_URL = "/user/login/"

@pytest.fixture
def create_user():
    user = get_user_model().objects.create_user(
        email="testuser@example.com",
        password="strong_password123",
        username="testuser"
    )
    return user

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_login_success(api_client, create_user):
    
    login_data = {
        "email": "testuser@example.com",
        "password": "strong_password123"
    }

    response = api_client.post(LOGIN_URL, login_data)

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data
    assert "access_token_expiration" in response.data
    assert "refresh_token_expiration" in response.data

@pytest.mark.django_db
def test_login_invalid_credentials(api_client, create_user):
    login_data = {
        "email": "testuser@example.com",
        "password": "wrongpassword"
    }

    response = api_client.post(LOGIN_URL, login_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data.get("error") == "Email or Password is not Valid"

@pytest.mark.django_db
def test_login_missing_email(api_client):
    login_data = {
        "password": "somepassword"
    }

    response = api_client.post(LOGIN_URL, login_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data
    assert "email" in response.data["errors"]

@pytest.mark.django_db
def test_login_missing_password(api_client):
    login_data = {
        "email": "testuser@example.com"
    }

    response = api_client.post(LOGIN_URL, login_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data
    assert "password" in response.data["errors"]

@pytest.mark.django_db
def test_login_invalid_email_format(api_client):
    login_data = {
        "email": "invalid-email-format",
        "password": "somepassword"
    }

    response = api_client.post(LOGIN_URL, login_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data
    assert "email" in response.data["errors"]
