"""
Views for the authentication application.

This module contains API views for user registration
and login functionality.

The views create authentication tokens and return
user information after successful authentication.
"""
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from auth_app.api.serializers import LoginSerializer
from .serializers import RegisterSerializer

def build_auth_response(user):
    """
    Build authentication response data.
    Creates or retrieves an authentication token for the user
    and returns the user information required by the API.
    Args: user: Authenticated User instance.
    Returns: dict: Authentication token and user information.
    """
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "fullname": user.fullname,
        "email": user.email,
        "user_id": user.id,
    }


class RegisterView(APIView):
    """
    API view for user registration.
    Handles creation of new user accounts.
    After successful registration, an authentication token
    and user data are returned.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Register a new user.
        Validates incoming registration data,
        creates a user and returns authentication data.
        Args: request: HTTP request containing registration data.
        Returns: Response: Created user data with authentication token.
        Status Codes: 201: User successfully created.
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(build_auth_response(user), 
                        status=status.HTTP_201_CREATED,)


class LoginView(APIView):
    """
    API view for user authentication.
    Authenticates users using email and password.
    Returns an authentication token on success.
    """
    def post(self, request):
        """
        Authenticate a user.
        Validates login credentials and returns authentication information.
        Args: request: HTTP request containing login data.
        Returns: Response: User data with authentication token.
        Status Codes: 200: Authentication successful.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return Response(
            build_auth_response(user),
            status=status.HTTP_200_OK,
        )