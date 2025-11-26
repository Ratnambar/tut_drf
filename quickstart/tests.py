from rest_framework.test import APITestCase
from django.contrib.auth.models import User
import json


# Create your tests here.

class UserViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username= "tester",
            email= "tester@example.com",
            password= "pass123"
        )

    def test_create_user(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpass123"
            }
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_retrieve_user(self):
        """Test retrieving a user by ID"""
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        # Make GET request to retrieve the user
        response = self.client.get(f'/api/users/{self.user.id}/')
        
        # Assert response status is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Assert response contains correct user data
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertIn('url', response.data)
        self.assertIn('groups', response.data)
        # Password should not be in response (write_only field)
        self.assertNotIn('password', response.data)

    def test_retrieve_user_unauthenticated(self):
        """Test that unauthenticated users cannot retrieve a user"""
        # Don't authenticate the client
        response = self.client.get(f'/api/users/{self.user.id}/')
        
        # Assert response status is 401 Unauthorized
        self.assertEqual(response.status_code, 401)

    def test_retrieve_nonexistent_user(self):
        """Test retrieving a user that doesn't exist"""
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        # Make GET request with a non-existent user ID
        nonexistent_id = 99999
        response = self.client.get(f'/api/users/{nonexistent_id}/')
        
        # Assert response status is 404 Not Found
        self.assertEqual(response.status_code, 404)