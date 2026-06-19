from django.contrib import admin

from kanban_app.models import (
    Board,
    Task,
    Comment,
)

admin.site.register(Board)
admin.site.register(Task)
admin.site.register(Comment)