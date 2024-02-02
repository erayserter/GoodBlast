from django.test import TestCase

from leaderboard.serializers import LeaderboardSerializer
from tournament.models import UserTournamentGroup, Tournament, TournamentGroup
from user.models import User


class LeaderboardSerializerTest(TestCase):
    def test_leaderboard_serializer(self):
        user = User.objects.create(username="testuser", country="US", password="testpassword")
        tournament = Tournament.objects.create(date="2021-01-01")
        tournament_group = TournamentGroup.objects.create(tournament=tournament)
        user_tournament_group = UserTournamentGroup.objects.create(user=user, group=tournament_group, score=100)

        serializer = LeaderboardSerializer(user_tournament_group)
        self.assertEqual(serializer.data, {
            'user': user.id,
            'country': user.country,
            'score': user_tournament_group.score
        })
