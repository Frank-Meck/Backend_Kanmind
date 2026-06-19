from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .serializers import RegisterSerializer
from auth_app.api.serializers import LoginSerializer


class RegisterView(APIView):
    """
    Handles user registration.

    Creates a new user and returns an authentication token
    together with user information.
    """

    def post(self, request):
        """
        Register a new user.

        Returns:
            Response: Token and user data on success.
        """
        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        token, _ = Token.objects.get_or_create(
            user=user
        )

        return Response(
            {
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )

class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data[
            "user"
        ]

        token, _ = Token.objects.get_or_create(
            user=user
        )

        return Response(
            {
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_200_OK,
        )
