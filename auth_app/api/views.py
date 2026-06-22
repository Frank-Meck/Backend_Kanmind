from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import LoginSerializer
from .serializers import RegisterSerializer


def build_auth_response(user):
    """
    Create the authentication response payload.
    """
    token, _ = Token.objects.get_or_create(
        user=user
    )

    return {
        "token": token.key,
        "fullname": user.fullname,
        "email": user.email,
        "user_id": user.id,
    }


class RegisterView(APIView):
    """
    Handles user registration.

    Creates a new user and returns an authentication
    token together with user information.
    """

    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        return Response(
            build_auth_response(user),
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    Handles user authentication.
    """

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

        return Response(
            build_auth_response(user),
            status=status.HTTP_200_OK,
        )
