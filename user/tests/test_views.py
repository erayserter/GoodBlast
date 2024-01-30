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


class LoginViewTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test',
            password='testpassword',
            country='GB'
        )
        self.user.save()

    def test_login_view_success(self):
        url = reverse('token_obtain_pair')

        data = {
            'username': 'test',
            'password': 'testpassword'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIsNotNone(response.data.get('access'))
        self.assertIsNotNone(response.data.get('refresh'))

    def test_login_view_invalid_credentials(self):
        url = reverse('token_obtain_pair')

        data = {
            'username': 'test',
            'password': 'wrongpassword'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get('detail'), 'No active account found with the given credentials')

    def test_login_refresh_view(self):
        url = reverse('token_obtain_pair')

        data = {
            'username': 'test',
            'password': 'testpassword'
        }

        response = self.client.post(url, data, format='json')

        url = reverse('token_refresh')

        data = {
            'refresh': response.data.get('refresh')
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('access'))


class UserDetailViewTestCase(APITestCase):
    def setUp(self):
        self.user = User(
            username='test',
            password='testpassword',
            coins=12760,
            country='TR',
            current_level=68
        )
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_get_user_detail(self):
        url = reverse('user-detail', kwargs={
            "username": self.user.username
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['coins'], self.user.coins)
        self.assertEqual(response.data['country'], self.user.country)
        self.assertEqual(response.data['current_level'], self.user.current_level)

    def test_get_user_detail_without_auth(self):
        self.client.logout()

        url = reverse('user-detail', kwargs={
            "username": self.user.username
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_another_user_detail(self):
        user2 = User.objects.create_user(
            username='test2',
            password='testpassword2',
            country='GB'
        )

        url = reverse('user-detail', kwargs={
            "username": user2.username
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user_success(self):
        url = reverse('user-detail', kwargs={
            "username": self.user.username
        })

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_another_user(self):
        user2 = User.objects.create_user(
            username='test2',
            password='testpassword2',
            country='GB'
        )

        url = reverse('user-detail', kwargs={
            "username": user2.username
        })

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
