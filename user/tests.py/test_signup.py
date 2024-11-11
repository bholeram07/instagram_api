import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse

SIGNUP_URL = reverse('signup-user')
User = get_user_model()

@pytest.fixture
def api_client():
    """Fixture to provide a DRF API client for tests."""
    return APIClient()

@pytest.fixture
def user_data():
    """Fixture to set up initial data for signup."""
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Bhole057p@",
        "confirm_password" : "Bhole057p@"
    }

@pytest.fixture(autouse=True)
def cleanup_users():
    """Fixture to clean up User data after each test."""
    yield  
    User.objects.all().delete()  
@pytest.mark.django_db
def test_signup_success(api_client, user_data):
    response = api_client.post(SIGNUP_URL, user_data)
    
   
    assert response.status_code == 201
    assert "message" in response.data
    assert response.data["message"] == "User Signup Successfully"
   
    user = User.objects.filter(email=user_data["email"]).first()
    assert user is not None
    assert user.username == user_data["username"]


    
@pytest.mark.django_db
def test_signup_invalid_data(api_client):
    invalid_data = {
        "username": "testuser",
        "email": "testuser@example.com",
    }
    
    response = api_client.post(SIGNUP_URL, invalid_data)
    
  
    assert response.status_code == 400
    assert "message" in response.data
    assert "password" in response.data["message"]  
