from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from tournament.models import TournamentGroup, UserTournamentGroup, Tournament
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


class UserDetailViewTest(APITestCase):
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


class UserUpdateProgressViewTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test',
            password='testpassword',
            country='GB'
        )
        self.client.force_authenticate(user=self.user)
        self.tournament = Tournament.objects.create(date=timezone.now().date())
        self.url = reverse('user-progress', kwargs={"username": self.user.username})

    def test_success(self):
        first_coins = self.user.coins
        first_level = self.user.current_level

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('coins'), first_coins + User.LEVEL_COMPLETE_COIN_REWARD)
        self.assertEqual(response.data.get('current_level'), first_level + 1)
        self.assertEqual(self.user.coins, first_coins + User.LEVEL_COMPLETE_COIN_REWARD)
        self.assertEqual(self.user.current_level, first_level + 1)

    def test_update_progress_in_tournament(self):
        group = TournamentGroup.objects.create(tournament=self.tournament)
        user_tournament_group = UserTournamentGroup.objects.create(user=self.user, group=group)

        first_score = user_tournament_group.score
        first_coins = self.user.coins

        response = self.client.post(self.url)

        user_tournament_group.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('coins'), first_coins + User.LEVEL_COMPLETE_COIN_REWARD)
        self.assertEqual(user_tournament_group.score, first_score + 1)
        self.assertEqual(self.user.coins, first_coins + User.LEVEL_COMPLETE_COIN_REWARD)
        self.assertEqual(user_tournament_group.score, first_score + 1)

    def test_update_progress_without_auth(self):
        self.client.logout()

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
