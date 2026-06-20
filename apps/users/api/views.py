from rest_framework.generics import CreateAPIView

from apps.users.models import User
from .serializers import RegisterSerializer


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
