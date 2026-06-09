from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from .serializers import RegisterSerializer
from auth_app.models import User


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
            Response: Token and user data on success,
            or validation errors on failure.
        """
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    """
    Authenticates a user and returns a token.
    """

    def post(self, request):
        """
        Validate login credentials and return token.

        Returns:
            200: Authentication successful
            400: Missing or invalid credentials
        """

        email = request.data.get("email")
        password = request.data.get("password")

        # ✅ Edge case validation (WICHTIG für PM-Tests)
        if not email:
            return Response(
                {"email": "This field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not password:
            return Response(
                {"password": "This field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "fullname": user.fullname,
            "email": user.email,
            "user_id": user.id
        }, status=status.HTTP_200_OK)
