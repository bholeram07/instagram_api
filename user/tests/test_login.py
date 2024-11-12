from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user.models import User



class LoginTestCase(TestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(username="testuser", password="Bhole057p@",email = "abc@gmail.com")
        self.user.is_verified = True  
        self.user.save()
        
    
        self.client = APIClient()
        
        
    
    
    def test_login(self):
        response = self.client.post(reverse('login'), {
            'email': 'abc@gmail.com',
            'password': 'Bhole057p@'
        })
        
      
        print("Login Response Status:", response.status_code)
        print("Login Response Data:", response.data)
        

        self.access_token = response.data.get('access')
        if not self.access_token:
            self.fail("Login did not return a token. Check if 'IsUserVerified' permission blocks unverified users.")
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)