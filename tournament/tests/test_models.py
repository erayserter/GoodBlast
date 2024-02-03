import random
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from tournament.models import Tournament, TournamentGroup, UserTournamentGroup
from user.models import User


class TournamentModelTest(TestCase):
    def test_create_daily_tournament(self):
        new_tournament = Tournament.create_daily_tournament()

        tomorrow = timezone.now().date() + timedelta(days=1)

        self.assertIsNotNone(new_tournament.id, "The tournament should be saved and have an ID.")
        self.assertEqual(new_tournament.date, tomorrow, "The tournament date should be set to tomorrow.")

    def test_get_current_tournament(self):
        today_tournament = Tournament(date=timezone.now().date())
        today_tournament.save()

        current_tournament = Tournament.get_current_tournament()

        self.assertEqual(current_tournament.id, today_tournament.id,
                         "The current tournament should match the one created for today.")


class TournamentGroupModelTests(TestCase):
    def setUp(self):
        self.tournament = Tournament.objects.create(date="2024-01-01")

    def test_get_ranks_reward(self):
        for reward_group in TournamentGroup.RANKING_REWARD_GROUPS:
            self.assertEqual(
                TournamentGroup.get_ranks_reward(reward_group["start"]),
                TournamentGroup.get_ranks_reward(reward_group["end"]),
                f"Rank {reward_group['start']}-{reward_group['end']} bucket should get the same reward."
            )
            self.assertEqual(
                TournamentGroup.get_ranks_reward(reward_group["end"]),
                reward_group["price"],
                f"Rank {reward_group['start']}-{reward_group['end']} should get a reward of {reward_group['price']}."
            )

    def test_is_eligible_for_reward(self):
        for reward_group in TournamentGroup.RANKING_REWARD_GROUPS:
            self.assertTrue(
                TournamentGroup.is_eligible_for_reward(reward_group["end"]),
                f"Rank {reward_group['end']} should be eligible for reward."
            )

        not_eligible = TournamentGroup.RANKING_REWARD_GROUPS[-1]["end"] + 1
        self.assertFalse(
            TournamentGroup.is_eligible_for_reward(not_eligible),
            f"Rank {not_eligible} should not be eligible for reward."
        )


class UserTournamentGroupModelTests(TestCase):
    def setUp(self):
        self.user = User(
            username='testuser',
            password='password',
            coins=1000,
            current_level=15
        )
        self.user.save()

        self.current_tournament = Tournament.objects.create(date=timezone.now().date())
        self.passed_tournament = Tournament.objects.create(date=timezone.now().date() - timedelta(days=1))
        self.future_tournament = Tournament.objects.create(date=timezone.now().date() + timedelta(days=1))

        self.before_entry_end_hour = timezone.now().replace(hour=Tournament.ENTRY_END_HOUR - 1)
        self.in_entry_end_hour = timezone.now().replace(hour=Tournament.ENTRY_END_HOUR)

    @patch('django.utils.timezone.now')
    def _enter_tournament_in_time(self, user, tournament, mock_now, time=timezone.now()):
        mock_now.return_value = time
        return UserTournamentGroup.enter_tournament(user, tournament)

    def test_enter_tournament(self):
        users_first_coins = self.user.coins
        user_tournament_group = self._enter_tournament_in_time(
            self.user,
            self.current_tournament,
            time=self.before_entry_end_hour
        )

        self.assertIsNotNone(user_tournament_group, "User should be able to enter the tournament.")
        self.assertEqual(self.user.coins, users_first_coins - Tournament.ENTRY_FEE,
                         "User's coins should be deducted by the entry fee.")
        self.assertEqual(user_tournament_group.score, 0, "User's score should be initialized to 0.")
        self.assertEqual(user_tournament_group.group.tournament, self.current_tournament)
        self.assertEqual(user_tournament_group.user, self.user)

    def test_update_score(self):
        user_tournament_group = self._enter_tournament_in_time(
            self.user,
            self.current_tournament,
            time=self.before_entry_end_hour
        )

        gained_score = 5

        new_score = user_tournament_group.update_score(gained_score)

        self.assertEqual(new_score, gained_score, "New score should be equal to the gained score.")
        self.assertEqual(user_tournament_group.score, gained_score, "User's score should be updated correctly.")

    def test_claim_reward(self):
        users_first_coins = self.user.coins
        user_tournament_group = self._enter_tournament_in_time(
            self.user,
            self.current_tournament,
            time=self.before_entry_end_hour
        )
        user_tournament_group.update_score(100)
        user_tournament_group.claim_reward(1)

        self.assertTrue(user_tournament_group.claimed_reward, "User should have claimed the reward.")
        expected_coins = users_first_coins - Tournament.ENTRY_FEE + TournamentGroup.get_ranks_reward(1)
        self.assertEqual(self.user.coins, expected_coins, "User's coins should be increased by the reward amount.")

    def test_claim_reward_multiple_times(self):
        user_tournament_group = self._enter_tournament_in_time(
            self.user,
            self.current_tournament,
            time=self.before_entry_end_hour
        )
        user_tournament_group.update_score(100)
        user_tournament_group.claim_reward(1)

        with self.assertRaises(ValueError):
            user_tournament_group.claim_reward(1)
