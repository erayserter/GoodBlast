from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from user.models import User


class UserCreateViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_success(self):
        url = reverse('user-create')

        data = {
            'username': 'test',
            'password': 'testpassword',
            'country': 'US',
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('username'), 'test')
        self.assertEqual(response.data.get('country'), 'US')
        self.assertEqual(response.data.get('current_level'), 1)
        self.assertEqual(response.data.get('coins'), 1000)

    def test_duplicate_username(self):
        User.objects.create_user(username='test', password='testpassword', country='US')

        url = reverse('user-create')

        data = {
            'username': 'test',
            'password': 'testpassword',
            'country': 'US',
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_country(self):
        url = reverse('user-create')

        data = {
            'username': 'test',
            'password': 'testpassword',
            'country': 'abc',
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
