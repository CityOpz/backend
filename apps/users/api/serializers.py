from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]

    def create(self, validated_data):

        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            role="CITIZEN",
        )

        user.set_password(validated_data["password"])

        user.save()

        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "role": self.user.role,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
        }

        return data