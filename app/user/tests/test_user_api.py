from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


# helper function to create a user
def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PublicUserAPITests(TestCase):
    """Test the users API ( Public )"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """test creating a user with valid payload is successful"""
        payload = {
            'email': 'test@tru.com',
            'password': 'testPass123',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists"""
        payload = {
            'email': 'test@tru.com',
            'password': 'testPass123',
            'name': 'Test duplicate'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@tru.com',
            'password': 'te',
            'name': 'Test password length'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """test that a token is created for the user"""
        payload = {
            'email': 'test@tru.com',
            'password': 'testPass123',
            'name': 'createTOken name'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_creds(self):
        """test token generation with invalid creds"""
        payload = {
            'email': 'test@tru.com',
            'password': 'testPass123',
            'name': 'createTOken name'
        }
        create_user(**payload)

        payload = {
            'email': 'test@tru.com',
            'password': 'testPass',
            'name': 'createTOken name'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_no_user(self):
        """test that token is not created if user doesn't exist"""
        payload = {
            'email': 'test@tru.com',
            'password': 'testPass123',
            'name': 'createTOken name'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_missing_field(self):
        """test that email and password are required"""
        payload = {
            'email': 'test@tru.com',
            'password': '',
            'name': 'createTOken name'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
