from django.shortcuts import get_object_or_404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, PermissionDenied

from django.contrib.auth import get_user_model

from kanban_app.models import (
    Board,
    Task,
    Comment,
)

from kanban_app.api.serializers import (
    BoardListSerializer,
    BoardDetailSerializer,
    BoardRetrieveSerializer,
    BoardUpdateResponseSerializer,
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    EmailCheckSerializer,
    CommentSerializer,
    CommentCreateSerializer,
)

from kanban_app.api.permissions import (
    IsBoardMemberOrOwner,
    IsBoardOwner,
    IsTaskBoardMember,
    IsTaskCreatorOrBoardOwner,
    IsCommentAuthor,
)


User = get_user_model()


class BoardListView(
    generics.ListCreateAPIView
):

    permission_classes = [
        IsAuthenticated
    ]

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

        serializer.is_valid(
            raise_exception=True
        )

        self.perform_create(serializer)

        return self.create_response(
            serializer.instance
        )

    def create_response(self, board):

        return Response(
            BoardListSerializer(board).data,
            status=status.HTTP_201_CREATED
        )


class BoardDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

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

    def update(
        self,
        request,
        *args,
        **kwargs
    ):

        serializer = self.get_update_serializer(
            request,
            kwargs
        )

        serializer.is_valid(
            raise_exception=True
        )

        self.perform_update(serializer)

        return Response(
            BoardUpdateResponseSerializer(
                serializer.instance
            ).data
        )

    def get_update_serializer(
        self,
        request,
        kwargs
    ):

        partial = kwargs.pop(
            "partial",
            request.method == "PATCH"
        )

        return self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial
        )

    def destroy(
        self,
        request,
        *args,
        **kwargs
    ):

        instance = self.get_object()

        self.perform_destroy(instance)

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class EmailCheckView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        email = request.query_params.get(
            "email"
        )

        error = self.validate_email(email)

        if error:
            return Response(
                {"error": error},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = self.find_user(email)

        if not user:
            return Response(
                {"error": "Email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            EmailCheckSerializer(user).data,
            status=status.HTTP_200_OK,
        )

    def validate_email(self, email):

        if not email:
            return "Email is required."

        try:
            validate_email(email)

        except ValidationError:
            return "Invalid email format."

        return None

    def find_user(self, email):

        try:
            return User.objects.get(
                email=email
            )

        except User.DoesNotExist:
            return None


class TaskCreateView(
    generics.CreateAPIView
):

    serializer_class = (
        TaskCreateSerializer
    )

    permission_classes = [
        IsAuthenticated
    ]

    def create(
        self,
        request,
        *args,
        **kwargs
    ):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        task = serializer.save(
            creator=request.user
        )

        return Response(
            TaskSerializer(task).data,
            status=status.HTTP_201_CREATED
        )


class AssignedToMeView(
    generics.ListAPIView
):

    serializer_class = TaskSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return Task.objects.filter(
            assignee=self.request.user
        )


class ReviewingView(
    generics.ListAPIView
):

    serializer_class = TaskSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return Task.objects.filter(
            reviewer=self.request.user
        )


class TaskDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Task.objects.all()

    def get_serializer_class(self):

        if self.request.method == "PATCH":
            return TaskUpdateSerializer

        return TaskSerializer

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

    def get_object(self):

        obj = super().get_object()

        self.check_object_permissions(
            self.request,
            obj
        )

        return obj

    def update(
        self,
        request,
        *args,
        **kwargs
    ):

        serializer = self.get_update_serializer(
            request,
            kwargs
        )

        serializer.is_valid(
            raise_exception=True
        )

        self.perform_update(
            serializer
        )

        return Response(
            TaskSerializer(
                serializer.instance
            ).data
        )

    def get_update_serializer(
        self,
        request,
        kwargs
    ):

        partial = kwargs.pop(
            "partial",
            False
        )

        return self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial
        )


class CommentListCreateView(
    generics.ListCreateAPIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def get_task(self):

        return get_object_or_404(
            Task,
            pk=self.kwargs["task_id"]
        )

    def get_queryset(self):

        task = self.get_task()

        self.check_member(
            task
        )

        return task.comments.all()

    def check_member(
        self,
        task
    ):

        if not task.board.members.filter(
            id=self.request.user.id
        ).exists():

            raise PermissionDenied()

    def get_serializer_class(self):

        if self.request.method == "POST":
            return CommentCreateSerializer

        return CommentSerializer

    def get_serializer_context(self):

        context = (
            super()
            .get_serializer_context()
        )

        context["task"] = self.get_task()

        return context


    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        comment = serializer.save()

        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )

class CommentDeleteView(
    generics.DestroyAPIView
):

    queryset = Comment.objects.all()

    permission_classes = [
        IsAuthenticated,
        IsCommentAuthor,
    ]

    def get_queryset(self):

        return Comment.objects.filter(
            task_id=self.kwargs["task_id"]
        )
