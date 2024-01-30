from rest_framework import serializers

from django_countries.serializers import CountryFieldMixin

from user.models import User


class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    coins = serializers.IntegerField(read_only=True)
    current_level = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "country", "coins", "current_level", "created_at", "updated_at"]
        lookup_field = 'username'


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", ]
