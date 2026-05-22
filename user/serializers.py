from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    object = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = [
            "object",
            "id",
            "email",
            "name",
            "is_active",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = ["object", "id", "date_joined"]

    def get_object(self, _):
        return "user"


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = models.User
        fields = ["email", "name", "password", "password_confirm"]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = models.User(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data
