from rest_framework.test import APITestCase

from user.models import User
from user.serializers import UserSerializer


class UserCreateSerializerTest(APITestCase):
    def test_valid_data(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'country': 'US',
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})

    def test_duplicate_username(self):
        User.objects.create_user(username='existinguser', password='testpassword', country='US')

        data = {
            'username': 'existinguser',
            'password': 'testpassword',
            'country': 'US',
        }

        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['username'][0], 'user with this username already exists.')

    def test_invalid_country(self):
        data = {
            'username': 'existinguser',
            'password': 'testpassword',
            'country': 'abc',
        }

        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['country'][0].code, 'invalid_choice')

    def test_create(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'country': 'US',
        }

        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.create(serializer.validated_data)
        self.assertEqual(user.username, 'testuser')
