from rest_framework import serializers

from tournament.models import UserTournamentGroup


class LeaderboardSerializer(serializers.ModelSerializer):
    country = serializers.CharField(source='user.country')

    class Meta:
        model = UserTournamentGroup
        fields = ['user', 'country', 'score']
        read_only_fields = ['user', 'country', 'score']
