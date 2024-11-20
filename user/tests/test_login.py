import os
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client

os.environ['DJANGO_SETTINGS_MODULE'] = 'instagram_api.settings'

User = get_user_model()

@pytest.fixture
def user_data():
    """Fixture to create a user in the database for testing."""
    user_data = {
        'username': 'testuser',
        'password': 'Bhole057p@',
        'email': 'testuser@example.com',
        'is_verified' :True
    }
    user = User.objects.create_user(**user_data)
    return user

@pytest.fixture
def client():
    """Fixture to provide the test client."""
    return Client()

@pytest.mark.django_db(transaction=True)
def test_login_success(client, user_data):
    """Test case for successful login."""
    login_data = {
        "username": user_data.username,
        "password": "Bhole057p@",  
    }
    response = client.post(reverse('login'), login_data)
    
    assert response.status_code == 200  

@pytest.mark.django_db(transaction=True)
def test_login_invalid_password(client, user_data):
    """Test case for login with an invalid password."""
    login_data = {
        "username": user_data.username,
        "password": "WrongPassword123",  # Incorrect password
    }
    response = client.post(reverse('login'), login_data)
    
    assert response.status_code == 400  #

@pytest.mark.django_db(transaction=True)
def test_login_invalid_username(client):
    """Test case for login with a non-existent username."""
    login_data = {
        "username": "nonexistentuser",  # Username that doesn't exist
        "password": "Bhole057p@",  # Any password
    }
    response = client.post(reverse('login'), login_data)
    
    assert response.status_code == 400  # Invalid username should return 400
    assert "Invalid username or password" in response.content.decode()  # Adjust based on your error message
