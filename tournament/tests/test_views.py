from datetime import timedelta, datetime
from unittest import mock

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from tournament.models import Tournament, UserTournamentGroup, TournamentGroup
from user.models import User


class EnterTournamentViewTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User(
            username='test',
            password='testpassword',
            country='US',
            current_level=Tournament.USER_LEVEL_REQUIREMENT,
            coins=Tournament.ENTRY_FEE
        )
        self.user.save()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('enter-tournament')

    def test_success(self):
        Tournament.objects.create(date=timezone.now().date())

        mocked_datetime = timezone.make_aware(datetime.combine(timezone.now().date(), datetime.min.time()))
        mocked_datetime += timedelta(hours=Tournament.ENTRY_END_HOUR - 1)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = mocked_datetime
            response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_failure_due_to_entry_time_passed(self):
        Tournament.objects.create(date=timezone.now().date())

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value.hour = Tournament.ENTRY_END_HOUR + 1
            response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failure_due_to_insufficient_coins(self):
        self.user.coins = Tournament.ENTRY_FEE - 1
        self.user.save()

        Tournament.objects.create(date=timezone.now().date())

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value.hour = Tournament.ENTRY_END_HOUR - 1
            response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failure_due_to_level_requirement(self):
        self.user.current_level = Tournament.USER_LEVEL_REQUIREMENT - 1
        self.user.save()

        Tournament.objects.create(date=timezone.now().date())

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value.hour = Tournament.ENTRY_END_HOUR - 1
            response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failure_due_to_already_entered(self):
        Tournament.objects.create(date=timezone.now().date())

        mocked_datetime = timezone.make_aware(datetime.combine(timezone.now().date(), datetime.min.time()))
        mocked_datetime += timedelta(hours=Tournament.ENTRY_END_HOUR - 1)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = mocked_datetime
            response = self.client.post(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failure_due_to_no_user(self):
        self.client.logout()

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ClaimTournamentRewardViewTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.old_coins = 2345
        self.user = User(
            username='test',
            password='testpassword',
            country='US',
            current_level=Tournament.USER_LEVEL_REQUIREMENT,
            coins=self.old_coins
        )
        self.user.save()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('claim-tournament-reward')

    def test_success(self):
        now = timezone.now()

        tournament = Tournament.objects.create(date=now.date())
        previous_tournament = Tournament.objects.create(date=now.date() - timezone.timedelta(days=1))
        UserTournamentGroup.enter_tournament(self.user, tournament)
        UserTournamentGroup.enter_tournament(self.user, previous_tournament)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now + timezone.timedelta(days=1)
            response = self.client.post(self.url, data={'tournament': tournament.id})

        new_coins = TournamentGroup.get_ranks_reward(1) + self.old_coins - Tournament.ENTRY_FEE * 2

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('coins'), new_coins)
        self.assertEqual(self.user.coins, new_coins)

    def test_success_claim_all(self):
        now = timezone.now()

        tournament = Tournament.objects.create(date=(now - timezone.timedelta(days=1)).date())
        tournament2 = Tournament.objects.create(date=now.date())
        group = TournamentGroup.objects.create(tournament=tournament)
        group2 = TournamentGroup.objects.create(tournament=tournament2)
        UserTournamentGroup.objects.create(user=self.user, group=group, score=1)
        UserTournamentGroup.objects.create(user=self.user, group=group2, score=1)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now + timezone.timedelta(days=1)
            response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('coins'), TournamentGroup.get_ranks_reward(1) * 2 + self.old_coins)
        self.assertEqual(self.user.coins, TournamentGroup.get_ranks_reward(1) * 2 + self.old_coins)

    def test_failure_due_to_already_claimed(self):
        now = timezone.now()
        tournament = Tournament.objects.create(date=now.date())
        group = TournamentGroup.objects.create(tournament=tournament)
        UserTournamentGroup.objects.create(user=self.user, group=group, score=1, claimed_reward=True)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now + timezone.timedelta(days=1)
            response = self.client.post(self.url, data={
                'tournament': tournament.id
            })

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_failure_due_to_no_completed_groups(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_failure_due_to_no_tournament_found(self):
        response = self.client.post(self.url, data={
            'tournament': 1
        })

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_failure_due_to_no_user(self):
        self.client.logout()

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_failure_due_to_no_eligible_rank(self):
        now = timezone.now()
        tournament = Tournament.objects.create(date=now.date())
        group = TournamentGroup.objects.create(tournament=tournament)
        UserTournamentGroup.objects.create(user=self.user, group=group, score=1)

        for i in range(2, TournamentGroup.RANKING_REWARD_GROUPS[-1]['end'] + 2):
            UserTournamentGroup.objects.create(user=User.objects.create(username=f'test{i}'), group=group, score=i)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now + timezone.timedelta(days=1)
            response = self.client.post(self.url, data={
                'tournament': tournament.id
            })

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
