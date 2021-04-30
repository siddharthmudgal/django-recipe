from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientAPITest(TestCase):
    """test the public API's for ingredient"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required_for_ingredient(self):
        """test login req to access ingredients endpoints"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITest(TestCase):
    """test the private API's for ingredients"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@tru.com',
            'testPass123'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """test to retrieve a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """test that ingredients belong to authenticated user"""
        user2 = get_user_model().objects.create_user(
            'test2@tru.com',
            'testPass123'
        )

        Ingredient.objects.create(user=user2, name='Vinegar')

        ing = Ingredient.objects.create(user=self.user, name='Turmeric')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ing.name)

    def test_create_ingredients(self):
        """test that authenticated user is able to create ingredient"""
        payload = {
            'name': 'Chilli'
        }
        res = self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.all().filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_ingredient_with_invalid(self):
        """test that ingredient creation fails with invalid details"""
        payload = {
            'name': ''
        }
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """test filtering tags by those assigend to reci"""
        ing1 = Ingredient.objects.create(user=self.user, name='Breakfast')
        ing2 = Ingredient.objects.create(user=self.user, name='Lunch')

        recipe = Recipe.objects.create(
            title='Coriander eggs on toast',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe.ingredients.add(ing1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ing1)
        serializer2 = IngredientSerializer(ing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """tags returned should be unique"""
        ing1 = Ingredient.objects.create(user=self.user, name='Breakfast')
        ing2 = Ingredient.objects.create(user=self.user, name='Lunch')

        recipe1 = Recipe.objects.create(
            title='Coriander eggs on toast',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe1.ingredients.add(ing1)

        recipe2 = Recipe.objects.create(
            title='Coriander on toast',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe2.ingredients.add(ing1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ing1)
        serializer2 = IngredientSerializer(ing2)

        self.assertIn(serializer1.data, res.data)
        self.assertEqual(len(res.data), 1)
        self.assertNotIn(serializer2.data, res.data)
