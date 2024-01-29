from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user.serializers import UserSerializer
from user.models import User


class UserCreate(CreateAPIView):
    permission_classes = [AllowAny, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UpdateProgress(GenericAPIView):
    permission_classes = [AllowAny, ]  # TODO: authentication olacaksa permissionlari duzenle.
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    def get(self, request, *args, **kwargs):  # TODO: birden fazla bolum gecilebiliyorsa gectigi bolum sayisini al.
        user = self.get_object()
        user.complete_level()
        return Response({
            "new_coins": user.coins,
            "current_level": user.current_level,
        })
