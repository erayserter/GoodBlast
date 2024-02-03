from django.db.models import Window, F
from django.db.models.functions import Rank
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tournament.models import Tournament, UserTournamentGroup, TournamentGroup


class EnterTournament(GenericAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        user = request.user

        if timezone.now().hour >= Tournament.ENTRY_END_HOUR:
            return Response({
                "message": f"Tournament entry hour {Tournament.ENTRY_END_HOUR} UTC has passed."
            }, status=status.HTTP_400_BAD_REQUEST)

        if user.coins < Tournament.ENTRY_FEE:
            return Response({
                "message": f"You should have at least {Tournament.ENTRY_FEE} coins to enter the tournament."
            }, status=status.HTTP_400_BAD_REQUEST)

        if user.current_level < Tournament.USER_LEVEL_REQUIREMENT:
            return Response({
                "message": f"You should be at least level {Tournament.USER_LEVEL_REQUIREMENT} to enter the tournament."
            }, status=status.HTTP_400_BAD_REQUEST)

        tournament = Tournament.get_current_tournament()

        if UserTournamentGroup.objects.filter(user=user, group__tournament=tournament).exists():
            return Response({
                "message": "You have already entered the tournament."
            }, status=status.HTTP_400_BAD_REQUEST)

        tournament_group = UserTournamentGroup.enter_tournament(user, tournament)

        return Response({
            "tournament": tournament.id,
            "group": tournament_group.id,
            "score": tournament_group.score
        }, status=status.HTTP_200_OK)


class ClaimTournamentReward(GenericAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        tournament_id = request.data.get("tournament")
        user = request.user

        users_passed_completed_groups = UserTournamentGroup.objects.filter(
            claimed_reward=False,
            group__tournament__date__lt=timezone.now().date(),
        ).annotate(
            rank=Window(
                expression=Rank(),
                order_by=F('score').desc(),
                partition_by=F('group')
            )
        ).filter(rank__lte=TournamentGroup.RANKING_REWARD_GROUPS[-1]["end"])

        users_passed_completed_groups = users_passed_completed_groups.filter(pk__in=users_passed_completed_groups, user=user)

        if tournament_id:
            users_passed_completed_groups = users_passed_completed_groups.filter(group__tournament__id=tournament_id)

        if not users_passed_completed_groups:
            return Response({
                "message": f"There is no tournament you have ever completed and not received the rewards."
            }, status=status.HTTP_404_NOT_FOUND)

        for group in users_passed_completed_groups:
            rank = group.get_rank()
            group.claim_reward(rank)

        user.refresh_from_db(fields=('coins',))

        return Response({
            "message": "Successfully claimed tournament rewards.",
            "coins": user.coins
        })
