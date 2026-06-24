"""
Admin configuration for the authentication application.

This module registers the custom User model in the Django admin
interface and defines how user information is displayed.
"""
from django.contrib import admin

from auth_app.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin configuration for the custom User model.
    Defines which user fields are visible in the Django admin
    user list view.
    """
    list_display = (
        "id",
        "email",
        "fullname",
        "is_staff",
    )