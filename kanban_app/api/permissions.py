from rest_framework.permissions import BasePermission


class IsBoardMemberOrOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            obj.owner == request.user
            or obj.members.filter(id=request.user.id).exists()
        )


class IsBoardOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user