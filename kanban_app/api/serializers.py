from rest_framework import serializers

from auth_app.models import User
from kanban_app.models import Board, Task


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