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
        coins = 18650
        current_level = 15

        user = User(
            username="testuser",
            country="US",
            password="testpassword",
            coins=coins,
            current_level=current_level
        )
        user.complete_level()

        self.assertEqual(user.current_level, current_level + 1)
        self.assertEqual(user.coins, coins + User.LEVEL_COMPLETE_COIN_REWARD)

    def test_gain_coin(self):
        coins = 18650
        gained_coin = 100

        user = User(username="testuser", country="US", password="testpassword", coins=coins)
        user.gain_coin(gained_coin)
        self.assertEqual(user.coins, coins + gained_coin)

    def test_lose_coin(self):
        coins = 18650
        lost_coin = 100

        user = User(username="testuser", country="US", password="testpassword", coins=coins)
        user.lose_coin(100)
        self.assertEqual(user.coins, coins - lost_coin)

    def test_not_enough_coin(self):
        coins = 50
        lost_coin = 100

        user = User(username="testuser", country="US", password="testpassword", coins=coins)

        with self.assertRaises(ValueError):
            user.lose_coin(lost_coin)
