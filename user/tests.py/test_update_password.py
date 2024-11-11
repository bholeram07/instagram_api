import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse



User = get_user_model()
@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_update_password_success(api_client):
    user = User.objects.create_user(email="testuser@example.com", password="old_password123", username="testuser")
    
   
    login_data = {
        'email': 'testuser@example.com',
        'password': 'old_password123'
    }

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    data = {
        'current_password': 'old_password123',
        'new_password': 'new_password123'
    }

    response = api_client.put(
        'user/update-password/',
        data,
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
 
    assert response.status_code == status.HTTP_202_ACCEPTED

  
    user.refresh_from_db()
    assert user.check_password('new_password123')

@pytest.mark.django_db
def test_update_password_invalid_current_password(api_client):
    user = User.objects.create_user(email="testuser@example.com", password="old_password123", username="testuser")
    api_client.login(email="testuser@example.com", password="old_password123")

    data = {
        'current_password': 'wrong_password',
        'new_password': 'new_password123'
    }

    url = reverse('update-password')
    response = api_client.put(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

 
    user.refresh_from_db()
    assert user.check_password('old_password123')

@pytest.mark.django_db
def test_update_password_missing_fields(api_client):
    user = User.objects.create_user(email="testuser@example.com", password="old_password123", username="testuser")
    
    api_client.login(email="testuser@example.com", password="old_password123")

 
    data = {
        'new_password': 'new_password123'
    }
    response = api_client.put('/update-password/', data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    user.refresh_from_db()
    assert user.check_password('old_password123')

@pytest.mark.django_db
def test_update_password_not_authenticated(api_client):
    user = User.objects.create_user(email="testuser@example.com", password="old_password123", username="testuser")

    
    data = {
        'current_password': 'old_password123',
        'new_password': 'new_password123'
    }

    response = api_client.put('/update-password/', data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

