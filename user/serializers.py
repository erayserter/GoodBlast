from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from user.models import User


class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "country", "coins", "current_level", "created_at", "updated_at"]
        lookup_field = 'username'

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('User with this username already exists.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            country=validated_data['country'],
        )
        user.save()
        return user
