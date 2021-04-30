from django.test import TestCase
from django.contrib.auth import get_user_model
from .. import models


def sample_user(email='test@tru.com', password='testPass123'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email address is success"""
        email = 'test@tru.com'
        password = 'testPassword123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """test that the email is normalized for a new user"""
        email = 'test@TRU.com'
        user = get_user_model().objects.create_user(email, 'testpassword')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """validate the email of a to be created user"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                None,
                'testPassword123'
            )

    def test_create_new_super_user(self):
        """Test creating a new super user"""
        user = get_user_model().objects.create_superuser(
            'test@tru.com',
            'testPassword123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """test the ingredient representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)
