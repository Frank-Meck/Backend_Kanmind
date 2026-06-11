
from os import path
from django.urls import path
from kanban_app.api.views import BoardDetailView, BoardListView


urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path("boards/<int:pk>/", BoardDetailView.as_view(),
         name="board-detail",),
]
