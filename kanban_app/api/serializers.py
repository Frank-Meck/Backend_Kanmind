"""
Serializers for the Kanban application.

This module contains Django REST Framework serializers
for users, boards, tasks and comments.

Serializers are responsible for converting model data
into API responses and validating incoming API data.
"""

from rest_framework import serializers

from auth_app.models import User
from kanban_app.models import (
    Board,
    Task,
    Comment,
)

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user information.
    Provides basic user data for API responses.
    """
    class Meta:
        """
        Meta configuration for UserSerializer.
        Defines the User model and exposed fields.
        """
        model = User
        fields = [
            "id",
            "email",
            "fullname",
        ]


class TaskPreviewSerializer(serializers.ModelSerializer):
    """
    Serializer for task preview information. Used when displaying tasks 
    inside a board. Includes assigned users and comment count.
    """
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        """
        Meta configuration for TaskPreviewSerializer.
        """
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        """
        Return the number of comments for a task.
        Args: obj: Task instance.
        Returns: int: Number of related comments.
        """
        return obj.comments.count()


class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for board list responses. Provides summarized board information 
    including member count and task statistics.
    """
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        """
        Meta configuration for BoardListSerializer.
        """
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

    def get_member_count(self, obj):
        """
        Return number of board members.
        Args: obj: Board instance.
        Returns: int: Member count.
        """
        return obj.members.count()

    def get_ticket_count(self, obj):
        """
        Return total number of tasks.
        Args: obj: Board instance.
        Returns: int: Task count.
        """
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """
        Return amount of unfinished tasks.
        Args: obj: Board instance.
        Returns: int: Number of tasks with status 'to-do'.
        """
        return obj.tasks.filter(
            status="to-do"
        ).count()

    def get_tasks_high_prio_count(self, obj):
        """
        Return amount of high priority tasks.
        Args: obj: Board instance.
        Returns: int: Number of high priority tasks.
        """
        return obj.tasks.filter(
            priority="high"
        ).count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating boards. Handles board members and #
    assigns the current user as board owner.
    """
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        """
        Meta configuration for BoardDetailSerializer.
        """
        model = Board
        fields = [
            "title",
            "members",
        ]

    def create(self, validated_data):
        """
        Create a new board. Extracts members, creates the board and
        assigns members afterwards.
        Args: validated_data: Validated serializer data.
        Returns: Board: Created board instance.
        """
        members = validated_data.pop(
            "members",
            []
        )
        board = self.create_board(
            validated_data
        )
        self.add_members(
            board,
            members
        )
        return board

    def create_board(self, validated_data):
        """
        Create board object. The current request user becomes the owner.
        Args: validated_data: Board data.
        Returns: Board: Created board.
        """
        return Board.objects.create(
            owner=self.context["request"].user,
            **validated_data
        )

    def add_members(self, board, members):
        """
        Add users to a board. Ensures the owner is always included
        as board member.
        Args: board: Board instance.
              members: List of users.
        """
        board.members.add(board.owner)

        if members:
            board.members.add(
                *members
            )

    def update(self, instance, validated_data):
        """
        Update an existing board. Updates title and members.
        Args: instance: Existing board object.
              validated_data: Updated data.
        Returns: Board: Updated board.
        """
        members = validated_data.pop(
            "members",
            None
        )
        instance.title = validated_data.get(
            "title",
            instance.title
        )
        instance.save()

        if members is not None:
            self.update_members(
                instance,
                members
            )

        return instance

    def update_members(
        self,
        instance,
        members
    ):
        """
        Replace board members. Makes sure the owner remains a member.
        Args: instance: Board object.
              members: New members list.
        """
        if instance.owner not in members:
            members.append(
                instance.owner
            )
        instance.members.set(
            members
        )


class BoardRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed board retrieval.
    Includes owner, members and all related tasks.
    """
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskPreviewSerializer(many=True, read_only=True)

    class Meta:
        """
        Meta configuration for BoardRetrieveSerializer.
        """
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]


class BoardUpdateResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for board update responses. Returns updated board information
    including owner and member details.
    """
    owner_data = UserSerializer(source="owner", read_only=True)
    members_data = UserSerializer(source="members", many=True, read_only=True)

    class Meta:
        """
        Meta configuration for BoardUpdateResponseSerializer.
        """
        model = Board
        fields = [
            "id",
            "title",
            "owner_data",
            "members_data",
        ]


class EmailCheckSerializer(serializers.ModelSerializer):
    """
    Serializer for checking user email information. Returns basic user 
    information after a successful email lookup.
    """
    class Meta:
        """
        Meta configuration for EmailCheckSerializer. Defines the User model 
        and exposed fields.
        """
        model = User
        fields = [
            "id",
            "email",
            "fullname",
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new tasks. Validates that assigned users and 
    reviewers belong to the selected board before creating a task.
    """
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        """
        Meta configuration for TaskCreateSerializer. Defines the Task model 
        and fields required for creating a task.
        """
        model = Task
        fields = [
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "due_date",
        ]

    def validate_board(self, board):
        """
        Validate that the current user is a board member.
        Args: board: Board instance.
        Returns: Board: Validated board object.
        Raises: ValidationError: If user is not a board member.
        """
        request = self.context["request"]

        if not board.members.filter(
            id=request.user.id
        ).exists():
            raise serializers.ValidationError(
                "You are not a member of this board."
            )
        return board

    def validate(self, attrs):
        """
        Validate assigned users. Checks if assignee and reviewer belong
        to the selected board.
        Args: attrs: Task data.
        Returns: dict: Validated task data.
        """
        board = attrs["board"]
        self.validate_user(
            board,
            attrs.get("assignee_id"),
            "assignee_id"
        )
        self.validate_user(
            board,
            attrs.get("reviewer_id"),
            "reviewer_id"
        )
        return attrs

    def validate_user(
        self,
        board,
        user_id,
        field
    ):
        """
        Validate that a user is part of the board.
        Args: board: Board instance.
              user_id: ID of the user to check.
              field: Serializer field name.
        Raises: ValidationError: If user is not a board member.
        """
        if user_id is None:
            return
        if not board.members.filter(
            id=user_id
        ).exists():
            raise serializers.ValidationError(
                {
                    field:
                    "User must be board member."
                }
            )

    def create(self, validated_data):
        """
        Create a new task. Converts assignee and reviewer IDs into User objects
        before saving the task.
        Args: validated_data: Validated task data.
        Returns: Task: Created task instance.
        """
        assignee = self.get_user(
            validated_data.pop(
                "assignee_id",
                None
            )
        )
        reviewer = self.get_user(
            validated_data.pop(
                "reviewer_id",
                None
            )
        )
        return Task.objects.create(
            assignee=assignee,
            reviewer=reviewer,
            **validated_data
        )

    def get_user(self, user_id):
        """
        Retrieve a User object by ID.
        Args: user_id: User primary key.
        Returns: User | None: User instance or None.
        """
        if user_id is None:
            return None
        return User.objects.get(
            id=user_id
        )


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed task responses.Provides task information including 
    assigned users, board information and comment count.
    """
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        """
        Meta configuration for TaskSerializer. Defines the Task model and 
        response fields.
        """
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        """
        Return number of comments belonging to a task.
        Args: obj: Task instance.
        Returns: int: Amount of related comments.
        """
        return obj.comments.count()


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing tasks. Handles updating task fields and 
    validates that assigned users belong to the task board.
    """
    assignee_id = serializers.IntegerField(required=False, allow_null=True,)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True,)

    class Meta:
        """
        Meta configuration for TaskUpdateSerializer. Defines writable task fields.
        """
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "due_date",
        ]

    def validate(self, attrs):
        """
        Validate assigned users before updating a task. Checks whether assignee
        and reviewer are members of the related board.
        Args: attrs: Updated task data.
        Returns: dict: Validated data.
        """
        board = self.instance.board
        self.validate_user(
            board,
            attrs.get("assignee_id"),
            "assignee_id"
        )
        self.validate_user(
            board,
            attrs.get("reviewer_id"),
            "reviewer_id"
        )
        return attrs

    def validate_user(
        self,
        board,
        user_id,
        field
    ):
        """
        Validate if a user belongs to a board.
        Args: board: Related board instance.
              user_id: User ID to validate.
              field:Serializer field name.
        Raises: ValidationError: If user is not a board member.
        """
        if user_id is None:
            return

        if not board.members.filter(
            id=user_id
        ).exists():
            raise serializers.ValidationError(
                {
                    field:
                    "User must be board member."
                }
            )

    def update(
        self,
        instance,
        validated_data
    ):
        """
        Update a task instance. Updates user relations separately and then
        applies remaining task fields.
        Args: instance: Existing Task object.
              validated_data: Updated task data.
        Returns: Task: Updated task instance.
        """
        self.update_users(
            instance,
            validated_data
        )
        for attr, value in validated_data.items():
            setattr(
                instance,
                attr,
                value
            )
        instance.save()
        return instance

    def update_users(
        self,
        instance,
        data
    ):
        """
        Update task user assignments.Handles changes to assignee and reviewer fields.
        Args: instance: Task instance.
              data: Update data dictionary.
        """
        if "assignee_id" in data:
            instance.assignee_id = data.pop(
                "assignee_id"
            )
        if "reviewer_id" in data:
            instance.reviewer_id = data.pop(
                "reviewer_id"
            )


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comment responses.Returns comment information including author,
    creation date and content.
    """
    author = serializers.CharField(source="author.fullname", read_only=True)

    class Meta:
        """
        Meta configuration for CommentSerializer.
        """
        model = Comment
        fields = [
            "id",
            "created_at",
            "author",
            "content",
        ]


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments. Validates comment content and 
    automatically assigns task and author from request context.
    """
    class Meta:
        """
        Meta configuration for CommentCreateSerializer.
        """
        model = Comment
        fields = [
            "content",
        ]

    def validate_content(self, value):
        """ 
        Validate comment content. Prevents creating empty comments.
        Args: value: Submitted comment text.
        Returns: str: Clean comment content.
        Raises: ValidationError: If content is empty.
        """
        if not value.strip():
            raise serializers.ValidationError(
                "Content cannot be empty."
            )
        return value

    def create(self, validated_data):
        """
        Create a new comment. Uses task and user from serializer context.
        Args: validated_data: Validated comment data.
        Returns: Comment: Created comment instance.
        """
        return Comment.objects.create(
            task=self.context["task"],
            author=self.context["request"].user,
            **validated_data
        )