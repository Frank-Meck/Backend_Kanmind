"""
Authentication serializers for the auth application.

This module contains serializers for user registration
and login processes using Django REST Framework.
"""
from auth_app.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates registration data, checks password confirmation
    and creates a new user account.
    """
    password = serializers.CharField(
        write_only=True
    )

    repeated_password = serializers.CharField(
        write_only=True
    )


    class Meta:
        """
        Meta configuration for RegisterSerializer.

        Defines the User model and fields required
        during registration.
        """
        model = User

        fields = (
            "fullname",
            "email",
            "password",
            "repeated_password",
        )

    def validate(self, attrs):
        """
        Validate registration data.

        Checks whether the password and repeated password
        values are identical.

        Args:
            attrs: Submitted registration data.

        Returns:
            dict: Validated registration data.

        Raises:
            ValidationError:
                If passwords do not match.
        """

        if attrs["password"] != attrs["repeated_password"]:

            raise serializers.ValidationError(
                "Passwords do not match"
            )

        return attrs

    def create(self, validated_data):
        """
        Create a new user account.

        Removes the repeated password field and creates
        the user using the custom UserManager.

        Args:
            validated_data: Validated user data.

        Returns:
            User: Newly created user instance.
        """
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
    """
    Serializer for user login.

    Authenticates users using email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):
        """
        Authenticate user credentials.
        Uses Django authentication backend to verify
        email and password.
        Args: attrs: Submitted login data.
        Returns:dict: Login data including authenticated user.
        Raises: ValidationError: If credentials are invalid.
        """
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