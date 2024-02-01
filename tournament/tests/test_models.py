import random
from datetime import timedelta, datetime
from unittest.mock import patch

import pytz
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

    def test_is_finished_with_past_tournament(self):
        past_tournament = Tournament(date=timezone.now().date() - timedelta(days=1))
        past_tournament.save()

        self.assertTrue(past_tournament.is_finished(), "Past tournament should be marked as finished.")

    def test_is_finished_with_future_tournament(self):
        future_tournament = Tournament(date=timezone.now().date() + timedelta(days=1))
        future_tournament.save()

        self.assertFalse(future_tournament.is_finished(), "Future tournament should not be marked as finished.")

    def test_is_finished_with_current_tournament(self):
        today_tournament = Tournament(date=timezone.now().date())
        today_tournament.save()

        self.assertFalse(today_tournament.is_finished(), "Current day tournament should not be marked as finished.")


class TournamentGroupModelTests(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(date="2024-01-01")

    def test_has_empty_place_initially_true(self):
        group = TournamentGroup.objects.create(tournament=self.tournament)

        self.assertTrue(group.has_empty_place, "Newly created group should have empty places.")

    def test_has_empty_place_after_adding_users(self):
        group = TournamentGroup.objects.create(tournament=self.tournament)

        for i in range(TournamentGroup.GROUP_SIZE):
            user = User.objects.create_user(username=f"testuser_{i}", country="US", password="testpassword")
            UserTournamentGroup.objects.create(user=user, group=group)

        self.assertFalse(group.has_empty_place, "Group should have no empty places after reaching GROUP_SIZE.")

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

    def test_enter_tournament_success(self):
        users_first_coins = self.user.coins
        user_tournament_group = self._enter_tournament_in_time(
            self.user,
            self.current_tournament,
            time=self.before_entry_end_hour
        )

        self.assertIsNotNone(user_tournament_group, "User should be able to enter the tournament.")
        self.assertEqual(self.user.coins, users_first_coins - Tournament.ENTRY_FEE,
                         "User's coins should be deducted by the entry fee.")

    def test_enter_tournament_failure_due_to_insufficient_coins(self):
        self.user.coins = Tournament.ENTRY_FEE - 1
        self.user.save()

        user_tournament_group = self._enter_tournament_in_time(
            self.user,
            self.current_tournament,
            time=self.before_entry_end_hour
        )

        self.assertIsNone(user_tournament_group,
                          "User with insufficient coins should not be able to enter the tournament.")

    def test_enter_tournament_failure_due_to_level_requirement(self):
        self.user.current_level = Tournament.USER_LEVEL_REQUIREMENT - 1
        self.user.save()

        user_tournament_group = self._enter_tournament_in_time(
            self.user,
            self.current_tournament,
            time=self.before_entry_end_hour
        )

        self.assertIsNone(user_tournament_group,
                          "User with level lower than the requirement should not be able to enter the tournament.")

    def test_enter_tournament_failure_due_to_passed_tournament(self):
        user_tournament_group = self._enter_tournament_in_time(
            self.user,
            self.passed_tournament,
            time=self.before_entry_end_hour
        )

        self.assertIsNone(user_tournament_group,
                          "User should not be able to enter a passed tournament.")

    def test_enter_tournament_failure_due_to_future_tournament(self):
        user_tournament_group = self._enter_tournament_in_time(
            self.user,
            self.future_tournament,
            time=self.before_entry_end_hour
        )

        self.assertIsNone(user_tournament_group,
                          "User should not be able to enter a future tournament.")

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
        user_tournament_group.claim_reward()

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
        user_tournament_group.claim_reward()

        with self.assertRaises(ValueError):
            user_tournament_group.claim_reward()

    def test_get_group_with_ranks(self):
        scores = [random.randint(1, 1000) for _ in range(10)]

        tournament_group = TournamentGroup.objects.create(tournament=self.current_tournament)

        for index, score in enumerate(scores):
            user = User.objects.create_user(username=f"testuser_{index}", country="US", password="testpassword")
            UserTournamentGroup.objects.create(user=user, group=tournament_group, score=score)

        tournament_group_with_ranks = UserTournamentGroup.get_group_with_ranks(tournament_group)
        ranked = tournament_group_with_ranks.order_by("-score").values_list("score", flat=True)

        self.assertListEqual(list(ranked), sorted(scores, reverse=True),
                             "Users should be ranked by their score in the group.")


