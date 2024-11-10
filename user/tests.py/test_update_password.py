import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse


# Use the custom User model
User = get_user_model()
@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_update_password_success(api_client):
    # Create a test user
    user = User.objects.create_user(email="testuser@example.com", password="old_password123", username="testuser")
    
    # Login the user
    login_data = {
        'email': 'testuser@example.com',
        'password': 'old_password123'
    }

    # Obtain the refresh token (access token is also in the payload)
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # Prepare the data for password update
    data = {
        'current_password': 'old_password123',
        'new_password': 'new_password123'
    }
    
    # Make the PUT request with Authorization header
    response = api_client.put(
        'user/update-password/',
        data,
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
 
    assert response.status_code == status.HTTP_202_ACCEPTED

    # Ensure the password has been updated in the database
    user.refresh_from_db()
    assert user.check_password('new_password123')

@pytest.mark.django_db
def test_update_password_invalid_current_password(api_client):
    # Create a test user
    user = User.objects.create_user(email="testuser@example.com", password="old_password123", username="testuser")
    
    # Login the user
    api_client.login(email="testuser@example.com", password="old_password123")

    # Prepare the data with an incorrect current password
    data = {
        'current_password': 'wrong_password',
        'new_password': 'new_password123'
    }

    # Make the PUT request to update the password
    url = reverse('update-password')
    response = api_client.put(url, data, format='json')

    # Check that the response status code is 400 Bad Request
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Ensure the password has not been changed
    user.refresh_from_db()
    assert user.check_password('old_password123')

@pytest.mark.django_db
def test_update_password_missing_fields(api_client):
    # Create a test user
    user = User.objects.create_user(email="testuser@example.com", password="old_password123", username="testuser")
    
    # Login the user
    api_client.login(email="testuser@example.com", password="old_password123")

    # Prepare the data with missing current password
    data = {
        'new_password': 'new_password123'
    }

    # Make the PUT request to update the password
    response = api_client.put('/update-password/', data, format='json')

    # Check that the response status code is 400 Bad Request
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Ensure the password has not been changed
    user.refresh_from_db()
    assert user.check_password('old_password123')

@pytest.mark.django_db
def test_update_password_not_authenticated(api_client):
    # Create a test user
    user = User.objects.create_user(email="testuser@example.com", password="old_password123", username="testuser")

    # Prepare the data for password update
    data = {
        'current_password': 'old_password123',
        'new_password': 'new_password123'
    }

    # Make the PUT request to update the password without logging in
    response = api_client.put('/update-password/', data, format='json')

    # Check that the response status code is 401 Unauthorized
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

