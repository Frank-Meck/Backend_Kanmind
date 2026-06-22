from rest_framework import serializers

from auth_app.models import User
from kanban_app.models import Board, Task, Comment


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "fullname",
        ]


class TaskPreviewSerializer(serializers.ModelSerializer):

    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    comments_count = serializers.SerializerMethodField()

    class Meta:
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
        return obj.comments.count()


class BoardListSerializer(serializers.ModelSerializer):

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    owner_id = serializers.IntegerField(
        source="owner.id",
        read_only=True
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()


class BoardDetailSerializer(serializers.ModelSerializer):

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Board
        fields = [
            "title",
            "members",
        ]

    def create(self, validated_data):
        members = validated_data.pop("members", [])

        request = self.context["request"]

        board = Board.objects.create(
            owner=request.user,
            **validated_data
        )

        # Owner immer Mitglied
        board.members.add(request.user)

        # weitere Mitglieder
        if members:
            board.members.add(*members)

        return board

    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)

        instance.title = validated_data.get(
            "title",
            instance.title
        )

        instance.save()

        if members is not None:

            # Owner darf niemals entfernt werden
            if instance.owner not in members:
                members.append(instance.owner)

            instance.members.set(members)

        return instance


class BoardRetrieveSerializer(serializers.ModelSerializer):

    owner_id = serializers.IntegerField(
        source="owner.id",
        read_only=True
    )

    members = UserSerializer(
        many=True,
        read_only=True
    )

    tasks = TaskPreviewSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]


class BoardUpdateResponseSerializer(serializers.ModelSerializer):

    owner_data = UserSerializer(
        source="owner",
        read_only=True
    )

    members_data = UserSerializer(
        source="members",
        many=True,
        read_only=True
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_data",
            "members_data",
        ]


class EmailCheckSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "fullname",
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    reviewer_id = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    class Meta:
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
        request = self.context["request"]

        if not board.members.filter(
            id=request.user.id
        ).exists():
            raise serializers.ValidationError(
                "You are not a member of this board."
            )

        return board

    def validate(self, attrs):
        board = attrs["board"]
        if not board:
            return attrs

        assignee_id = attrs.get("assignee_id")
        reviewer_id = attrs.get("reviewer_id")

        if assignee_id is not None:
            if not board.members.filter(
                id=assignee_id
            ).exists():
                raise serializers.ValidationError(
                    {
                        "assignee_id":
                        "User must be board member."
                    }
                )

        if reviewer_id is not None:
            if not board.members.filter(
                id=reviewer_id
            ).exists():
                raise serializers.ValidationError(
                    {
                        "reviewer_id":
                        "User must be board member."
                    }
                )

        return attrs

    def create(self, validated_data):
        assignee_id = validated_data.pop(
            "assignee_id",
            None,
        )

        reviewer_id = validated_data.pop(
            "reviewer_id",
            None,
        )

        assignee = None
        reviewer = None

        if assignee_id is not None:
            assignee = User.objects.get(
                id=assignee_id
            )

        if reviewer_id is not None:
            reviewer = User.objects.get(
                id=reviewer_id
            )

        return Task.objects.create(
            assignee=assignee,
            reviewer=reviewer,
            **validated_data,
        )


class TaskWriteSerializer(
    serializers.ModelSerializer
):
    assignee_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    reviewer_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    class Meta:
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


class TaskSerializer(serializers.ModelSerializer):

    assignee = UserSerializer(
        read_only=True
    )

    reviewer = UserSerializer(
        read_only=True
    )

    comments_count = serializers.SerializerMethodField()

    class Meta:
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
        return obj.comments.count()


class TaskUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    reviewer_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    class Meta:
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
        board = self.instance.board

        assignee_id = attrs.get("assignee_id")
        reviewer_id = attrs.get("reviewer_id")

        if assignee_id is not None:
            if not board.members.filter(
                id=assignee_id
            ).exists():
                raise serializers.ValidationError(
                    {
                        "assignee_id":
                        "User must be board member."
                    }
                )

        if reviewer_id is not None:
            if not board.members.filter(
                id=reviewer_id
            ).exists():
                raise serializers.ValidationError(
                    {
                        "reviewer_id":
                        "User must be board member."
                    }
                )

        return attrs

    def update(self, instance, validated_data):
        has_assignee = (
            "assignee_id" in validated_data
        )

        has_reviewer = (
            "reviewer_id" in validated_data
        )

        assignee_id = validated_data.pop(
            "assignee_id",
            None,
        )

        reviewer_id = validated_data.pop(
            "reviewer_id",
            None,
        )

        for attr, value in validated_data.items():
            setattr(
                instance,
                attr,
                value,
            )

        if has_assignee:
            instance.assignee_id = (
                assignee_id
            )

        if has_reviewer:
            instance.reviewer_id = (
                reviewer_id
            )

        instance.save()

        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(
        source="author.fullname",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "created_at",
            "author",
            "content",
        ]


class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            "content",
        ]

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Content cannot be empty."
            )

        return value

    def create(self, validated_data):
        task = self.context["task"]
        request = self.context["request"]

        return Comment.objects.create(
            task=task,
            author=request.user,
            **validated_data
        )
