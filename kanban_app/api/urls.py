

from django.urls import path
from kanban_app.api.views import BoardDetailView, BoardListView, EmailCheckView


urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path("boards/<int:pk>/", BoardDetailView.as_view(),
         name="board-detail",),
    path("email-check/", EmailCheckView.as_view()),
]
