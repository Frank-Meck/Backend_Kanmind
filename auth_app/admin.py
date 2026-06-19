from django.contrib import admin

from auth_app.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "fullname",
        "is_staff",
    )

    def fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}"
