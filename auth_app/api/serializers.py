from auth_app.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates the submitted registration data and
    creates a new user account.
    """

    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "fullname",
            "email",
            "password",
            "repeated_password",
        )

    def validate(self, attrs):
        """
        Ensure that both password fields match.
        """
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                "Passwords do not match"
            )

        return attrs

    def create(self, validated_data):
        password = validated_data.pop(
            "password"
        )

        validated_data.pop(
            "repeated_password"
        )

        return User.objects.create_user(
            password=password,
            **validated_data
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):
        user = authenticate(
            email=attrs["email"],
            password=attrs["password"]
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid credentials"
            )

        attrs["user"] = user
        return attrs