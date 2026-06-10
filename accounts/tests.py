from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import User

class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register')

    def test_successful_registration(self):
        data = {
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, data["email"])
