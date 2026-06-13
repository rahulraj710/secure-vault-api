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

    def test_invalid_email(self):
        data = {
            'email': 'testexample',
            'password': 'StrongPass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)

    def test_email_not_provided(self):
        data = {
            'password': 'StrongPass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
    
    def test_password_not_provided(self):
        data = {
            'email': 'text@example.com',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)

    def test_registration_with_duplicate_email(self):
        User.objects.create_user(email='test@example.com', password='pass')
        data = {
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)

    def test_password_not_returned_in_response(self):
        data = {
            'email': 'text@example.com',
            'password': 'StrongPass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = self.client.post(self.url, data)
        self.assertNotIn('password', response.data)


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('login')
        User.objects.create_user(email='test@example.com', password='pass')

    def test_successful_login(self):
        data = {
            'email': 'test@example.com',
            'password': 'pass'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh', response.data)
