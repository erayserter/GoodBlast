from django.test import TestCase

from user.models import User


class UserModelTest(TestCase):
    def test_create_user(self):
        username = "testuser"
        password = "testpassword"
        country = "US"

        user = User.objects.create_user(username=username, country=country, password=password)

        self.assertEqual(user.username, username)
        self.assertEqual(user.country.code, country)
        self.assertTrue(user.check_password(password))

    def test_gain_coin(self):
        user = User.objects.create_user(username="testuser", country="US", password="testpassword")
        user.gain_coin(100)
        self.assertEqual(user.coins, 1100)

    def test_lose_coin(self):
        user = User.objects.create_user(username="testuser", country="US", password="testpassword")
        user.lose_coin(100)
        self.assertEqual(user.coins, 900)
