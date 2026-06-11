from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import BoardUpdateResponseSerializer

from kanban_app.models import Board

from kanban_app.api.serializers import (
    BoardListSerializer,
    BoardDetailSerializer,
    BoardRetrieveSerializer,
)

from kanban_app.api.permissions import (
    IsBoardMemberOrOwner,
    IsBoardOwner,
)


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
