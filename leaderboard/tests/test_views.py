import random
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from django_countries import countries
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from leaderboard.views import RESULT_LIMIT
from tournament.models import Tournament, UserTournamentGroup, TournamentGroup
from user.models import User


class LeaderboardViewTest(APITestCase):
    user = None
    tournament = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.tournament = Tournament.objects.create(date=timezone.now().date())

        for i in range(RESULT_LIMIT + 10):
            cls.user = User(
                id=i,
                username=f'test{i}',
                password='testpassword',
                country=random.choice(list(countries.countries.keys())),
                current_level=Tournament.USER_LEVEL_REQUIREMENT,
                coins=Tournament.ENTRY_FEE
            )
            cls.user.save()
            user_tournament_group = UserTournamentGroup.enter_tournament(cls.user, cls.tournament)
            user_tournament_group.update_score(random.randint(1, 350))

    def setUp(self) -> None:
        self.client = APIClient()


class GlobalLeaderboardViewTest(LeaderboardViewTest):
    def test_success(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('global-leaderboard')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) <= RESULT_LIMIT)

    @patch('tournament.models.Tournament.get_current_tournament')
    def test_no_users(self, mock_tournament):
        self.client.force_authenticate(user=self.user)
        mock_tournament.return_value = Tournament.objects.create(date=timezone.now().date())

        url = reverse('global-leaderboard')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CountryLeaderboard(LeaderboardViewTest):
    def test_success(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('country-leaderboard')

        response = self.client.get(url)

        distinct_countries = set(list(map(lambda x: x['country'], response.data)))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(distinct_countries), 1)
        self.assertTrue(self.user.country in distinct_countries)
        self.assertTrue(len(response.data) <= RESULT_LIMIT)

    @patch('tournament.models.Tournament.get_current_tournament')
    def test_no_users(self, mock_tournament):
        self.client.force_authenticate(user=self.user)
        mock_tournament.return_value = Tournament.objects.create(date=timezone.now().date())

        url = reverse('country-leaderboard')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GroupLeaderboard(LeaderboardViewTest):
    def test_success(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('group-leaderboard')

        response = self.client.get(url)

        user_ids = list(map(lambda x: x['user'], response.data))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) <= TournamentGroup.GROUP_SIZE)
        self.assertTrue(self.user.id in user_ids)

    @patch('tournament.models.Tournament.get_current_tournament')
    def test_no_users(self, mock_tournament):
        self.client.force_authenticate(user=self.user)
        mock_tournament.return_value = Tournament.objects.create(date=timezone.now().date())

        url = reverse('group-leaderboard')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserGroupRankViewTest(LeaderboardViewTest):
    def test_success(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('user-group-rank')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['rank'] <= TournamentGroup.GROUP_SIZE)

    @patch('tournament.models.Tournament.get_current_tournament')
    def test_no_users(self, mock_tournament):
        self.client.force_authenticate(user=self.user)
        mock_tournament.return_value = Tournament.objects.create(date=timezone.now().date())

        url = reverse('user-group-rank')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)