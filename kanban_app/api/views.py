from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import BoardUpdateResponseSerializer, TaskCreateSerializer, TaskSerializer
from django.contrib.auth import get_user_model
from kanban_app.models import Board, Task
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.views import APIView, PermissionDenied


from kanban_app.api.serializers import (
    BoardListSerializer,
    BoardDetailSerializer,
    BoardRetrieveSerializer,
)

from kanban_app.api.permissions import (
    IsBoardMemberOrOwner,
    IsBoardOwner,
    IsTaskBoardMember,
    IsTaskCreatorOrBoardOwner,
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


class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def perform_create(self, serializer):
        board = serializer.validated_data["board"]

        if not board.members.filter(id=self.request.user.id).exists():
            raise PermissionDenied("Not a board member")

        serializer.save()


class AssignedToMeView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            assignee=self.request.user
        )


class ReviewingView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            reviewer=self.request.user
        )


class TaskDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [
                IsAuthenticated(),
                IsTaskCreatorOrBoardOwner(),
            ]

        return [
            IsAuthenticated(),
            IsTaskBoardMember(),
        ]
