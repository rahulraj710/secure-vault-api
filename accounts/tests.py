from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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
        self.user = User.objects.create_user(email='test@example.com', password='pass')

    def test_successful_login(self):
        data = {
            'email': 'test@example.com',
            'password': 'pass'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh', response.data)

    def test_user_does_not_exist(self):
        data = {
            'email': 'tester@example.com',
            'password': 'pass'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_invalid_credentials(self):
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
                
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['error'], 'Invalid credentials')
        self.assertEqual(self.user.is_locked, False)
        self.assertEqual(self.user.failed_login_attempts, 1)
        
    def test_lock_user_on_max_failed_attempts(self):
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        for _ in range(5):
            self.client.post(self.url, data)
        
        data = {
            'email': 'test@example.com',
            'password': 'pass'
        }
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['error'], 'Account temporarily locked')
        self.assertEqual(self.user.is_locked, True)
        self.assertEqual(self.user.failed_login_attempts, 5)

    def test_lock_reset_after_success(self):
        data = {
            'email': 'test@example.com',
            'password': 'password'
        }
        for _ in range(2):
            self.client.post(self.url, data)
        self.user.refresh_from_db()    
        self.assertEqual(self.user.failed_login_attempts, 2)
        
        data = {
            'email': 'test@example.com',
            'password': 'pass'
        }
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.is_locked, False)
        self.assertEqual(self.user.failed_login_attempts, 0)

    def test_account_auto_unlocks_after_duration(self):
        self.user.is_locked = True
        self.user.locked_at = timezone.now() - timedelta(minutes=16)
        self.user.save()
        response = self.client.post(self.url, {
            'email': 'test@example.com',
            'password': 'pass'
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_locked)

    def test_login_without_email(self):
        data = {'email': 'test@example.com'}
                
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 400)

    def test_login_without_password(self):
        data = {'email': 'test@example.com'}
                
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 400)
