from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tournament.models import Tournament, UserTournamentGroup
from user.permissions import IsPersonalAccountOrReadOnly
from user.serializers import UserSerializer
from user.models import User


class UserCreate(CreateAPIView):
    permission_classes = [AllowAny, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveDestroy(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, IsPersonalAccountOrReadOnly, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'


class UserUpdateProgress(APIView):
    permission_classes = [IsAuthenticated, IsPersonalAccountOrReadOnly, ]

    def post(self, request, *args, **kwargs):
        user = request.user
        user.complete_levels()

        tournament = Tournament.get_current_tournament()
        user_group = UserTournamentGroup.objects.filter(user=user, group__tournament=tournament)

        if user_group.exists():
            user_group = user_group.first()
            user_group.update_score()

        return Response({
            "coins": user.coins,
            "current_level": user.current_level,
        })
