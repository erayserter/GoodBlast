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

    def test_success(self):
        user = User(
            username='test',
            password='testpassword',
            country='US',
            current_level=Tournament.USER_LEVEL_REQUIREMENT,
            coins=Tournament.ENTRY_FEE
        )
        user.save()
        self.client.force_authenticate(user=user)

        Tournament.objects.create(date=timezone.now().date())

        url = reverse('enter-tournament')

        mocked_datetime = timezone.make_aware(datetime.combine(timezone.now().date(), datetime.min.time()))
        mocked_datetime += timedelta(hours=Tournament.ENTRY_END_HOUR - 1)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = mocked_datetime
            response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_failure_due_to_entry_time_passed(self):
        user = User(
            username='test',
            password='testpassword',
            country='US',
            current_level=Tournament.USER_LEVEL_REQUIREMENT,
            coins=Tournament.ENTRY_FEE
        )
        user.save()
        self.client.force_authenticate(user=user)

        Tournament.objects.create(date=timezone.now().date())

        url = reverse('enter-tournament')

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value.hour = Tournament.ENTRY_END_HOUR + 1
            response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failure_due_to_insufficient_coins(self):
        user = User(
            username='test',
            password='testpassword',
            country='US',
            current_level=Tournament.USER_LEVEL_REQUIREMENT,
            coins=Tournament.ENTRY_FEE - 1
        )
        user.save()
        self.client.force_authenticate(user=user)

        Tournament.objects.create(date=timezone.now().date())

        url = reverse('enter-tournament')

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value.hour = Tournament.ENTRY_END_HOUR - 1
            response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failure_due_to_level_requirement(self):
        user = User(
            username='test',
            password='testpassword',
            country='US',
            current_level=Tournament.USER_LEVEL_REQUIREMENT - 1,
            coins=Tournament.ENTRY_FEE
        )
        user.save()
        self.client.force_authenticate(user=user)

        Tournament.objects.create(date=timezone.now().date())

        url = reverse('enter-tournament')

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value.hour = Tournament.ENTRY_END_HOUR - 1
            response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failure_due_to_already_entered(self):
        user = User.objects.create(
            username='test',
            password='testpassword',
            country='US',
            current_level=Tournament.USER_LEVEL_REQUIREMENT,
            coins=Tournament.ENTRY_FEE * 2 + 1
        )
        self.client.force_authenticate(user=user)

        Tournament.objects.create(date=timezone.now().date())

        url = reverse('enter-tournament')

        mocked_datetime = timezone.make_aware(datetime.combine(timezone.now().date(), datetime.min.time()))
        mocked_datetime += timedelta(hours=Tournament.ENTRY_END_HOUR - 1)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = mocked_datetime
            response = self.client.post(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failure_due_to_no_user(self):
        url = reverse('enter-tournament')

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ClaimTournamentRewardViewTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_success(self):
        old_coins = 2345
        user = User(
            username='test',
            password='testpassword',
            country='US',
            current_level=Tournament.USER_LEVEL_REQUIREMENT,
            coins=old_coins
        )
        user.save()
        self.client.force_authenticate(user=user)

        now = timezone.now()

        tournament = Tournament.objects.create(date=now.date())
        group = TournamentGroup.objects.create(tournament=tournament)
        UserTournamentGroup.objects.create(user=user, group=group, score=1)

        url = reverse('claim-tournament-reward')

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now + timezone.timedelta(days=1)
            response = self.client.post(url, data={'tournament': tournament.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('coins'), TournamentGroup.get_ranks_reward(1) + old_coins)
        self.assertEqual(user.coins, TournamentGroup.get_ranks_reward(1) + old_coins)

    def test_success_claim_all(self):
        old_coins = 2356
        user = User(
            username='test',
            password='testpassword',
            country='US',
            current_level=Tournament.USER_LEVEL_REQUIREMENT,
            coins=old_coins
        )
        user.save()
        self.client.force_authenticate(user=user)

        now = timezone.now()

        tournament = Tournament.objects.create(date=(now - timezone.timedelta(days=1)).date())
        tournament2 = Tournament.objects.create(date=now.date())
        group = TournamentGroup.objects.create(tournament=tournament)
        group2 = TournamentGroup.objects.create(tournament=tournament2)
        UserTournamentGroup.objects.create(user=user, group=group, score=1)
        UserTournamentGroup.objects.create(user=user, group=group2, score=1)

        url = reverse('claim-tournament-reward')

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now + timezone.timedelta(days=1)
            response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('coins'), TournamentGroup.get_ranks_reward(1) * 2 + old_coins)
        self.assertEqual(user.coins, TournamentGroup.get_ranks_reward(1) * 2 + old_coins)

    def test_failure_due_to_no_completed_groups(self):
        user = User(
            username='test',
            password='testpassword',
            country='US',
            current_level=Tournament.USER_LEVEL_REQUIREMENT,
            coins=Tournament.ENTRY_FEE
        )
        user.save()
        self.client.force_authenticate(user=user)

        url = reverse('claim-tournament-reward')

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_failure_due_to_no_tournament_found(self):
        user = User.objects.create(
            username='test',
            password='testpassword',
            country='US',
            current_level=Tournament.USER_LEVEL_REQUIREMENT,
            coins=Tournament.ENTRY_FEE
        )
        self.client.force_authenticate(user=user)

        now = timezone.now()
        tournament = Tournament.objects.create(date=now.date())
        group = TournamentGroup.objects.create(tournament=tournament)
        UserTournamentGroup.objects.create(user=user, group=group, score=1)

        url = reverse('claim-tournament-reward')

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now + timezone.timedelta(days=1)
            response = self.client.post(url, data={
                'tournament': 0
            })

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_failure_due_to_no_user(self):
        url = reverse('claim-tournament-reward')

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
