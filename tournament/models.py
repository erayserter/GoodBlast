from django.db import models, transaction
from django.utils import timezone


class Tournament(models.Model):
    date = models.DateField()

    @classmethod
    def create_daily_tournament(cls):
        today = timezone.now().date()
        tournament = cls(date=today)
        tournament.save()
        return tournament

    @classmethod
    def get_current_tournament(cls):
        return cls.objects.get(date=timezone.now().date())

    def is_finished(self):
        return self.date < timezone.now().date()


class UserTournament(models.Model):
    ENTRY_FEE = 500
    USER_LEVEL_REQUIREMENT = 10
    ENTRY_END_HOUR = 12

    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    entered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tournament')

    @classmethod
    @transaction.atomic
    def enter_tournament(cls, user, tournament):
        utc_now = timezone.now()

        if (user.coins < cls.ENTRY_FEE
                or user.current_level < cls.USER_LEVEL_REQUIREMENT
                or utc_now < utc_now.replace(hour=12, minute=0, second=0, microsecond=0)):
            return None

        user.coins -= cls.ENTRY_FEE
        user_tournament = cls(
            user=user,
            tournament=tournament,
            entered_at=utc_now
        )
        user_tournament.save()
        user.save()

    def update_score(self, completed_level_count):
        self.score += completed_level_count
        self.save()
        return self.score
