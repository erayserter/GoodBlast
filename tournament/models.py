from datetime import timedelta

from django.db import models, transaction
from django.db.models import Window, F, Count
from django.db.models.functions import Rank
from django.utils import timezone


class Tournament(models.Model):
    ENTRY_FEE = 500
    USER_LEVEL_REQUIREMENT = 10
    ENTRY_END_HOUR = 12

    date = models.DateField()

    @classmethod
    def create_daily_tournament(cls):
        today_utc = timezone.now().date()
        tomorrow_utc = today_utc + timedelta(days=1)
        tournament = cls(date=tomorrow_utc)
        tournament.save()
        return tournament

    @classmethod
    def get_current_tournament(cls):
        return cls.objects.get(date=timezone.now().date())


class TournamentGroup(models.Model):
    GROUP_SIZE = 35
    RANKING_REWARD_GROUPS = [
        {
            "start": 1,
            "end": 1,
            "price": 5000
        },
        {
            "start": 2,
            "end": 2,
            "price": 3000
        },
        {
            "start": 3,
            "end": 3,
            "price": 2000
        },
        {
            "start": 4,
            "end": 10,
            "price": 1000
        }
    ]
    LEVEL_BUCKET_SIZE = 100

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='groups')
    level_bucket = models.IntegerField(default=0)

    @classmethod
    def get_ranks_reward(cls, rank):
        for reward_group in cls.RANKING_REWARD_GROUPS:
            if reward_group["start"] <= rank <= reward_group["end"]:
                return reward_group["price"]

        return 0

    @classmethod
    def is_eligible_for_reward(cls, rank):
        if cls.get_ranks_reward(rank) == 0:
            return False

        return True


class UserTournamentGroup(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    group = models.ForeignKey(TournamentGroup, on_delete=models.CASCADE, related_name='users')
    score = models.IntegerField(default=0)
    claimed_reward = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'group')

    @classmethod
    @transaction.atomic
    def enter_tournament(cls, user, tournament):
        user.coins -= tournament.ENTRY_FEE
        level_bucket = user.current_level // TournamentGroup.LEVEL_BUCKET_SIZE

        non_full_groups = tournament.groups\
            .filter(level_bucket=level_bucket)\
            .annotate(user_count=Count('users'))\
            .filter(user_count__lt=TournamentGroup.GROUP_SIZE)

        tournament_group = non_full_groups.first()

        if not tournament_group:
            tournament_group = TournamentGroup(tournament=tournament, level_bucket=level_bucket)

        user_tournament_group = cls(user=user, group=tournament_group)

        tournament_group.save()
        user_tournament_group.save()
        user.save()

        return user_tournament_group

    def get_rank(self):
        return UserTournamentGroup.objects.filter(
            group=self.group,
            score__gte=self.score
        ).distinct('score').count()

    def claim_reward(self, rank):
        if self.claimed_reward:
            raise ValueError("User has already claimed the reward.")

        if not TournamentGroup.is_eligible_for_reward(rank):
            raise ValueError("User is not eligible for the reward.")

        reward = TournamentGroup.get_ranks_reward(rank)

        self.user.coins += reward
        self.claimed_reward = True

        self.user.save()
        self.save()

    def update_score(self, completed_level_count=1):
        self.score += completed_level_count
        self.save()
        return self.score
