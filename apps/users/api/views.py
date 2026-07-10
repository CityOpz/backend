from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.models import User
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer