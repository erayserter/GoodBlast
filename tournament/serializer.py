from rest_framework import serializers

from tournament.models import Tournament


class TournamentIDSerializer(serializers.Serializer):
    tournament = serializers.IntegerField(min_value=1)

    def validate_tournament(self, value):
        if not Tournament.objects.filter(id=value).exists():
            raise serializers.ValidationError("Tournament does not exist with this ID.")
        return value
