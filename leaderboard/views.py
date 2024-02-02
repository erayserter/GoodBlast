from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from leaderboard.serializers import LeaderboardSerializer
from tournament.models import UserTournamentGroup, Tournament


RESULT_LIMIT = 1000


class GlobalLeaderboard(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        tournament = Tournament.get_current_tournament()
        groups = tournament.groups.all()
        scores = UserTournamentGroup.objects.filter(group__in=groups).order_by('-score')[:RESULT_LIMIT]

        if not scores:
            return Response({
                "message": "No users found in the active tournament."
            }, status=status.HTTP_404_NOT_FOUND)

        return Response(LeaderboardSerializer(scores, many=True).data, status=status.HTTP_200_OK)


class CountryLeaderboard(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        tournament = Tournament.get_current_tournament()
        groups = tournament.groups.all()
        scores = UserTournamentGroup.objects.filter(
            group__in=groups,
            user__country=request.user.country
        ).order_by('-score')[:RESULT_LIMIT]

        if not scores:
            return Response({
                "message": "No users found in the active tournament."
            }, status=status.HTTP_404_NOT_FOUND)

        return Response(LeaderboardSerializer(scores, many=True).data, status=status.HTTP_200_OK)


class GroupLeaderboard(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        tournament = Tournament.get_current_tournament()
        try:
            group = UserTournamentGroup.objects.get(user=request.user, group__tournament=tournament)
        except UserTournamentGroup.DoesNotExist:
            return Response({
                "message": "You are not in an active tournament group."
            }, status=status.HTTP_404_NOT_FOUND)

        scores = UserTournamentGroup.objects.filter(group=group).order_by('-score')[:RESULT_LIMIT]

        return Response(LeaderboardSerializer(scores, many=True).data, status=status.HTTP_200_OK)


class UserGroupRank(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        tournament = Tournament.get_current_tournament()

        try:
            group = UserTournamentGroup.objects.get(user=request.user, group__tournament=tournament)
        except UserTournamentGroup.DoesNotExist:
            return Response({
                "message": "You are not in an active tournament group."
            }, status=status.HTTP_404_NOT_FOUND)

        scores = UserTournamentGroup.objects.filter(group=group, score__gt=group.score).count() + 1
        return Response({
            "rank": scores
        }, status=status.HTTP_200_OK)
