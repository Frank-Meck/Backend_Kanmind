from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import BoardUpdateResponseSerializer
from django.contrib.auth import get_user_model
from kanban_app.models import Board
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.views import APIView


from kanban_app.api.serializers import (
    BoardListSerializer,
    BoardDetailSerializer,
    BoardRetrieveSerializer,
)

from kanban_app.api.permissions import (
    IsBoardMemberOrOwner,
    IsBoardOwner,
)

from kanban_app.api.serializers import (
    EmailCheckSerializer,
)


User = get_user_model()


class BoardListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BoardDetailSerializer

        return BoardListSerializer

    def get_queryset(self):
        return Board.objects.filter(
            members=self.request.user
        ).distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        board = Board.objects.get(
            id=serializer.instance.id
        )

        return Response(
            BoardListSerializer(board).data,
            status=201
        )


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()

    def get_serializer_class(self):

        if self.request.method == "GET":
            return BoardRetrieveSerializer

        return BoardDetailSerializer

    def get_permissions(self):

        if self.request.method == "DELETE":
            return [
                IsAuthenticated(),
                IsBoardOwner(),
            ]

        return [
            IsAuthenticated(),
            IsBoardMemberOrOwner(),
        ]

    def get_object(self):

        obj = super().get_object()

        self.check_object_permissions(
            self.request,
            obj
        )

        return obj

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop("partial", False)

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )

        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return Response(
            BoardUpdateResponseSerializer(
                serializer.instance
            ).data
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class EmailCheckView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")

        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"detail": "Email not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            "id": user.id,
            "email": user.email,
            "fullname": user.fullname
        })


class EmailCheckView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        email = request.query_params.get(
            "email"
        )

        if not email:
            return Response(
                {
                    "error": (
                        "Email is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_email(email)

        except ValidationError:
            return Response(
                {
                    "error": (
                        "Invalid email format."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(
                email=email
            )

        except User.DoesNotExist:
            return Response(
                {
                    "error": (
                        "Email not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmailCheckSerializer(
            user
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
