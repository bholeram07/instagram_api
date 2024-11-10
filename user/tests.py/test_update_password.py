import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import datetime

@pytest.mark.django_db
def test_update_password_success(client):

    user = get_user_model().objects.create_user(
        email="testuser@example.com", username="testuser", password="Bhole057p@"
    )
    
  
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    user.last_password_change = datetime.now()
    user.save()
    
    data = {
        "current_password": "Bhole057p@",
        "new_password": "Bhole057p@1"
    }
   

    url = reverse("update-password")  

    response = client.put(url, data, HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    
    user.refresh_from_db()
    assert user.check_password("Bhole057p@")
    assert user.last_password_change  

@pytest.mark.django_db
def test_update_password_invalid_current_password(client):
    # Create a test user
    user = get_user_model().objects.create_user(
        email="testuser@example.com", username="testuser", password="old_password123"
    )
    
    # Authenticate the user
    client.login(email="testuser@example.com", password="old_password123")
    

    data = {
        "current_password": "wrong_password123",  
        "new_password": "new_password123"
    }
    
    # URL for password update
    url = reverse("update-password")
    
    # Send request to update password
    response = client.put(url, data)
    
    # Check if the status code is 400 (incorrect current password)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Current password is incorrect."

@pytest.mark.django_db
def test_update_password_invalid_new_password(client):
    # Create a test user
    user = get_user_model().objects.create_user(
        email="testuser@example.com", username="testuser", password="old_password123"
    )
    
    # Authenticate the user
    client.login(email="testuser@example.com", password="old_password123")
    
    # Data for password update with invalid new password (e.g., too short)
    data = {
        "current_password": "old_password123",
        "new_password": "123"  # Invalid new password
    }
    
    # URL for password update
    url = reverse("update-password")
    
    # Send request to update password
    response = client.put(url, data)
    
    # Check if the status code is 400 (invalid new password)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "new_password" in response.data["error"]

@pytest.mark.django_db
def test_update_password_serializer_invalid(client):
    # Create a test user
    user = get_user_model().objects.create_user(
        email="testuser@example.com", username="testuser", password="old_password123"
    )
    
    # Authenticate the user
    client.login(email="testuser@example.com", password="old_password123")
    
    # Data for password update with missing current password
    data = {
        "new_password": "new_password123"
    }
    
    # URL for password update
    url = reverse("update-password")
    
    # Send request to update password
    response = client.put(url, data)
    
    # Check if the status code is 400 (invalid serializer)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "current_password" in response.data["error"]

