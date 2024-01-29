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
        self.assertEqual(user.current_level, 1)
        self.assertEqual(user.coins, 1000)
        self.assertTrue(user.check_password(password))

    def test_complete_level(self):
        user = User(
            username="testuser",
            country="US",
            password="testpassword",
            coins=1860,
            current_level=15
        )
        user.complete_level()

        self.assertEqual(user.current_level, 16)
        self.assertEqual(user.coins, 1960)

    def test_gain_coin(self):
        user = User(username="testuser", country="US", password="testpassword")
        user.gain_coin(100)
        self.assertEqual(user.coins, 1100)

    def test_lose_coin(self):
        user = User(username="testuser", country="US", password="testpassword")
        user.lose_coin(100)
        self.assertEqual(user.coins, 900)
