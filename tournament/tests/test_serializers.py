from django.test import TestCase

from tournament.models import Tournament
from tournament.serializer import TournamentIDSerializer


class TournamentIDSerializerTest(TestCase):
    def test_no_data(self):
        serializer = TournamentIDSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_valid_data(self):
        tournament = Tournament.objects.create(id=2, date='2021-01-01')
        serializer = TournamentIDSerializer(data={'tournament': tournament.id})
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        serializer = TournamentIDSerializer(data={'tournament': 'a'})
        self.assertFalse(serializer.is_valid())
