"""
Views for the Kanban application.

This module contains API views for managing boards,
tasks and comments.

The views handle CRUD operations, permissions and
validation for Kanban resources.
"""
from django.shortcuts import get_object_or_404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, PermissionDenied

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


class BoardListView(generics.ListCreateAPIView):
    """
    API view for listing and creating boards.
    GET: Returns all boards where the current user is a member.
    POST: Creates a new board with the current user as owner.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Return serializer depending on request method.
        Returns: Serializer: Board creation or list serializer.
        """
        if self.request.method == "POST":
            return BoardDetailSerializer
        return BoardListSerializer

    def get_queryset(self):
        """
        Return boards accessible by current user.
        Returns: QuerySet: Boards where user is a member.
        """
        return Board.objects.filter(
            members=self.request.user
        ).distinct()

    def create(self, request, *args, **kwargs):
        """
        Create a new board. Validates input data, saves the board and
        returns formatted response.
        Returns: Response: Created board data.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self.create_response(
            serializer.instance
        )

    def create_response(self, board):
        """
        Build board creation response.
        Args: board: Created Board instance.
        Returns: Response: Serialized board response.
        """
        return Response(
            BoardListSerializer(board).data,
            status=status.HTTP_201_CREATED
        )


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating and deleting boards.
    Supports:   - GET board details
                - UPDATE board data
                - DELETE board
    Permissions depend on requested action.
    """
    queryset = Board.objects.all()

    def get_serializer_class(self):
        """
        Select serializer based on HTTP method.
        Returns: Serializer: Retrieve or update serializer.
        """
        if self.request.method == "GET":
            return BoardRetrieveSerializer
        return BoardDetailSerializer

    def get_permissions(self):
        """
        Return permissions for current action. Board deletion requires ownership.
        Other actions require membership.
        Returns: list: Permission classes.
        """
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
        """
        Retrieve object and verify permissions.
        Returns: Board: Authorized board instance.
        """
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
        """
        Update an existing board.
        Returns: Response: Updated board information.
        """
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
        """
        Create serializer for update request.
        Args: request: HTTP request.
              kwargs:  Update options.
        Returns: Serializer: Configured update serializer.
        """
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
        """
        Delete a board.
        Returns: Response: Empty response with HTTP 204.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class EmailCheckView(APIView):
    """
    API view for checking existing email addresses. Used during board member
    selection to verify whether a user exists.
    """
    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):
        """
        Search user by email.
        Args: request: HTTP request containing email parameter.
        Returns: Response: User information or error message.
        """
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
        """
        Validate email format.
        Args: email: Email address.
        Returns: str | None: Error message or None.
        """
        if not email:
            return "Email is required."
        try:
            validate_email(email)
        except ValidationError:
            return "Invalid email format."
        return None

    def find_user(self, email):
        """
        Find user by email address.
        Args: email: Email address.
        Returns: User | None: User instance or None.
        """
        try:
            return User.objects.get(
                email=email
            )
        except User.DoesNotExist:
            return None


class TaskCreateView(generics.CreateAPIView):
    """
    API view for creating new tasks. Creates tasks inside boards and automatically
    assigns the current authenticated user as creator.
    """
    serializer_class = (TaskCreateSerializer)
    permission_classes = [IsAuthenticated]

    def create(
        self,
        request,
        *args,
        **kwargs
    ):
        """
        Create a new task. Validates task data, saves the task with the current
        user as creator and returns the created task.
        Args: request: HTTP request containing task data.
        Returns: Response: Created task data.
        """
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


class AssignedToMeView(generics.ListAPIView):
    """
    API view for listing assigned tasks. Returns all tasks where the current user
    is assigned as responsible person.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return tasks assigned to current user.
        Returns: QuerySet: Tasks assigned to request user.
        """
        return Task.objects.filter(
            assignee=self.request.user
        )

class ReviewingView(generics.ListAPIView):
    """
    API view for reviewing tasks. Returns all tasks where the current user
    is assigned as reviewer.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return tasks waiting for review.
        Returns: QuerySet: Tasks assigned to current user as reviewer.
        """
        return Task.objects.filter(
            reviewer=self.request.user
        )


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating and deleting tasks. Permissions depend on
    the requested action. Board members can edit tasks while only creators
    or board owners can delete them.
    """
    queryset = Task.objects.all()

    def get_serializer_class(self):
        """
        Select serializer depending on request type.
        Returns: Serializer: Update or read serializer.
        """
        if self.request.method == "PATCH":
            return TaskUpdateSerializer
        return TaskSerializer

    def get_permissions(self):
        """
        Return required permissions. DELETE requires creator or board owner.
        Other actions require board membership.
        Returns: list: Permission classes.
        """
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
        """
        Retrieve task and check permissions.
        Returns: Task: Authorized task instance.
        """
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
        """
        Update an existing task. Validates and saves changed task data.
        Returns: Response: Updated task information.
        """
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
        """
        Create serializer for task update.
        Args: request: HTTP request.
              kwargs: Update options.
        Returns: Serializer: Configured update serializer.
        """
        partial = kwargs.pop(
            "partial",
            False
        )
        return self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial
        )


class CommentListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating comments. Users can only access comments 
    of tasks belonging to boards they are members of.
    """
    permission_classes = [IsAuthenticated]

    def get_task(self):
        """
        Retrieve related task.
        Returns: Task: Task instance.
        Raises: Http404: If task does not exist.
        """
        task = get_object_or_404(
            Task,
            pk=self.kwargs["task_id"]
        )
        self.check_member(task)
        return task

    def get_queryset(self):
        """
        Return comments of selected task.
        Returns: QuerySet: Task comments.
        """
        task = self.get_task()
        self.check_member(
            task
        )
        return task.comments.all()

    def check_member(
        self,
        task
    ):
        """
        Check whether user belongs to task board.
        Args: task: Task instance.
        Raises: PermissionDenied: If user is not board member.
        """
        if not task.board.members.filter(
            id=self.request.user.id
        ).exists():
            raise PermissionDenied()

    def get_serializer_class(self):
        """
        Select serializer by request method.
        Returns: Serializer: Create or read serializer.
        """
        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentSerializer

    def get_serializer_context(self):
        """
        Add task to serializer context.
        Returns: dict: Extended serializer context.
        """
        context = (
            super()
            .get_serializer_context()
        )
        context["task"] = self.get_task()
        return context

    def create(
        self,
        request,
        *args,
        **kwargs
    ):
        """
        Create a new comment.
        Returns: Response: Created comment.
        """
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


class CommentDeleteView(generics.DestroyAPIView):
    """
    API view for deleting comments. Only the comment author is allowed to delete
    their own comments.
    """
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated, IsCommentAuthor,]

    def get_queryset(self):
        """
        Return comments belonging to task.
        Returns: QuerySet: Filtered comments.
        """
        return Comment.objects.filter(
            task_id=self.kwargs["task_id"]
        )

    def destroy(
        self,
        request,
        *args,
        **kwargs
    ):
        """
        Delete a comment. Validates task and comment IDs before deletion.
        Returns: Response: HTTP 204 after successful deletion.
        """
        task_id = self.kwargs.get("task_id")
        comment_id = self.kwargs.get("pk")
        if (
            not str(task_id).isdigit()
            or not str(comment_id).isdigit()
        ):
            return Response(
                {
                    "detail":
                    "Invalid task or comment id."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(
            request,
            *args,
            **kwargs
        )
