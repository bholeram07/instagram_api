import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'instagram_api.settings'
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
User = get_user_model()  

@pytest.fixture
def user_data():
    user_data = {
        'username': 'testuser',
        'password': 'Bhole057p@',
        'email': 'testuser@example.com',
    }
   
    user = User.objects.create(**user_data)
    assert User.objects.count() == 1
    assert User.objects.count() == 1
    assert User.objects.get(username=user_data['username'])

@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db(transaction=True)
def test_signup(client):
    data={
        "username" : "bholeram",
        "email" : "bhole@gmail.com",
        "password":"Bhole057p@",
        "confirm_password":"Bhole057p@"
    }
    response = client.post(reverse('signup'), data)
    assert response.status_code == 201
  

@pytest.mark.django_db(transaction=True)
def test_signup_duplicate_username(client):
    data={
        "username" : "bholeram",
        "email" : "bhole@gmail.com",
        "password":"Bhole057p@",
        "confirm_password":"Bhole057p@"
    }
    client.post(reverse('signup'), data)
    response = client.post(reverse('signup'), data)
    assert response.status_code == 400
    
