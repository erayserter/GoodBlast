from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from tournament.models import Tournament, UserTournamentGroup
from user.permissions import IsPersonalAccountOrReadOnly
from user.serializers import UserSerializer, UserUpdateProcessSerializer
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


class UserUpdateProgress(GenericAPIView):
    permission_classes = [IsAuthenticated, IsPersonalAccountOrReadOnly, ]
    serializer_class = UserUpdateProcessSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        completed_level_count = serializer.validated_data.get('completed_level_count')

        user = request.user
        user.complete_levels(completed_level_count)

        tournament = Tournament.get_current_tournament()
        user_group = UserTournamentGroup.objects.filter(user=user, tournament=tournament)

        if user_group.exists():
            user_group = user_group.first()
            user_group.update_progress(completed_level_count)

        return Response({
            "coins": user.coins,
            "current_level": user.current_level,
        })
