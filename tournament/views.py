from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tournament.models import Tournament, UserTournamentGroup


class EnterTournament(GenericAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        user = request.user
        tournament = Tournament.get_current_tournament()
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
            user=user,
            claimed_reward=False,
            group__tournament__date__lt=timezone.now().date()
        )

        if not users_passed_completed_groups:
            return Response({
                "message": "There is no tournament you have ever completed and not received the rewards."
            }, status=status.HTTP_404_NOT_FOUND)

        if not tournament_id:
            for group in users_passed_completed_groups:
                group.claim_reward()
        else:
            users_tournament_group = users_passed_completed_groups.filter(group__tournament__id=tournament_id)
            users_tournament_group.claim_reward()

        return Response({
            "message": "Successfully claimed tournament rewards.",
            "coins": user.coins
        })
