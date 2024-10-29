from rest_framework import serializers
from .models import User, Role
from .services import AuthService


class RoleReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]


# Read-Only Serializer
class UserReadSerializer(serializers.ModelSerializer):
    role = RoleReadSerializer()

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "role"]


# Write Serializer
class UserWriteSerializer(serializers.ModelSerializer):
    role_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "role_id"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        auth_service = AuthService()
        user = auth_service.register(validated_data)
        return user


class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class AuthUserSerializer(serializers.Serializer):
    user = UserReadSerializer()
    token = TokenSerializer()

    class Meta:
        fields = ["user", "token"]
