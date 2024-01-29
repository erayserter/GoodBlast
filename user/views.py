from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from user.serializers import UserSerializer
from user.models import User


class CreateUserAPIView(CreateAPIView):
    permission_classes = [AllowAny, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer
