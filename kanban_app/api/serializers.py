from rest_framework import serializers
from auth_app.models import User
from kanban_app.models import Board


class BoardListSerializer(serializers.ModelSerializer):

    member_count = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "member_count",
            "task_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_task_count(self, obj):
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
        fields = ["title", "members"]

    def create(self, validated_data):
        members = validated_data.pop("members", [])

        request = self.context["request"]

        # 🔥 OWNER MUSS HIER REIN
        board = Board.objects.create(
            owner=request.user,
            **validated_data
        )

        # owner immer member
        board.members.add(request.user)

        # zusätzliche members
        if members:
            board.members.add(*members)

        return board
