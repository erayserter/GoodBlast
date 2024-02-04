from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django_countries.fields import CountryField


class UserManager(BaseUserManager):
    def create_user(self, username, country, password=None):
        if not username:
            raise ValueError("Users must have a username")

        user = self.model(
            username=username,
            country=country
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, country, password=None):
        user = self.create_user(
            username,
            password=password,
            country=country
        )
        user.save(using=self._db)
        return user

    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class User(AbstractBaseUser):
    username = models.CharField(
        max_length=255,
        unique=True
    )
    coins = models.IntegerField(default=1000)
    country = CountryField()
    current_level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['country', ]

    LEVEL_COMPLETE_COIN_REWARD = 100

    def complete_levels(self, level_count=1):
        self.current_level += level_count
        self.coins += self.LEVEL_COMPLETE_COIN_REWARD * level_count
        self.save()

    def gain_coin(self, amount):
        self.coins += amount
        self.save()

    def lose_coin(self, amount):
        current_coin = self.coins - amount

        if current_coin < 0:
            raise ValueError("Not enough coins")

        self.coins = current_coin
        self.save()

    def __str__(self):
        return self.username
