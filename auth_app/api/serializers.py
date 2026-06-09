from auth_app.models import User
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
        """
        Create and return a new user instance.
        """
        validated_data.pop("repeated_password")

        user = User.objects.create_user(
            **validated_data
        )

        return user