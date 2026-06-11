from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from kanban_app.api.serializers import (
    BoardListSerializer,
    BoardDetailSerializer
)
from kanban_app.models import Board


class BoardListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BoardDetailSerializer
        return BoardListSerializer

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(members=user).distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)

        # 👇 WICHTIG: reload instance
        board = Board.objects.get(id=serializer.instance.id)

        return Response(
            BoardListSerializer(board).data,
            status=201,
            headers=headers
        )
