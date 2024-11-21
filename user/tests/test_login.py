import os
import pytest
from django.urls import reverse
from user.models import User
from django.test import Client

os.environ['DJANGO_SETTINGS_MODULE'] = 'instagram_api.settings'


@pytest.fixture
def user_data():
    """Fixture to create a user in the database for testing."""
    # Use create_user to ensure the password is hashed
    user = User.objects.create_user(
        email="abc@gmail.com",
        username="bholerampatidar",
        password="Bhole057p@",  # Ensure this matches during login
        is_private=False,
        is_verified=True,  # Ensure the user is verified
    )
    return user


@pytest.fixture
def client():
    """Fixture to provide the test client."""
    return Client()


@pytest.mark.django_db(transaction=True)
def test_login_success(client, user_data):
    """Test case for successful login."""
    login_data = {
        "email": "abc@gmail.com",
        "password": "Bhole057p@",  
    }
    response = client.post(reverse('login'), login_data)
    assert response.status_code == 200  


@pytest.mark.django_db(transaction=True)
def test_login_invalid_password(client, user_data):
    """Test case for login with an invalid password."""
    login_data = {
        "username": user_data.username,
        "password": "WrongPassword123",  
    }
    response = client.post(reverse('login'), login_data)
    assert response.status_code == 401 


@pytest.mark.django_db(transaction=True)
def test_login_invalid_username(client, user_data):
    """Test case for login with a non-existent username."""
    login_data = {
        "username": "nonexistentuser",
        "password": "Bhole057p@",  
    }
    response = client.post(reverse('login'), login_data)
    assert response.status_code == 401  
