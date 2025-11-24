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
