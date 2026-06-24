"""
Admin configuration for the Kanban application.

This module registers the Kanban models in the Django admin interface,
so they can be managed through the admin dashboard.
"""

from django.contrib import admin

from kanban_app.models import (
    Board,
    Task,
    Comment,
)

"""
Register the Board model.
Allows administrators to create, edit and manage Kanban boards
through the Django admin interface.
"""
admin.site.register(Board)


"""
Register the Task model.
Allows administrators to manage tasks, including their status,
priority, assignments and related board information.
"""
admin.site.register(Task)


"""
Register the Comment model.
Allows administrators to view and manage comments
created on tasks.
"""
admin.site.register(Comment)
