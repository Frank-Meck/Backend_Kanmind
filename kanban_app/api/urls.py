

from django.urls import path
from kanban_app.api.views import (
    BoardDetailView,
    BoardListView,
    EmailCheckView,
    AssignedToMeView,
    ReviewingView,
    TaskCreateView,
    TaskDetailView,
)


urlpatterns = [
    path("boards/", BoardListView.as_view(), name="board-list"),
    path("boards/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),
    path("email-check/", EmailCheckView.as_view()),

    path(
        "tasks/assigned-to-me/",
        AssignedToMeView.as_view(),
        name="assigned-to-me",
    ),

    path(
        "tasks/reviewing/",
        ReviewingView.as_view(),
        name="reviewing",
    ),

    path(
        "tasks/",
        TaskCreateView.as_view(),
        name="task-create",
    ),

    path(
        "tasks/<int:pk>/",
        TaskDetailView.as_view(),
        name="task-detail",
    ),
]