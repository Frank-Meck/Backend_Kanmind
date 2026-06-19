from rest_framework.permissions import BasePermission


class IsBoardOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBoardMemberOrOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            obj.owner == request.user
            or obj.members.filter(id=request.user.id).exists()
        )


class IsTaskBoardMember(BasePermission):

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        return obj.board.members.filter(
            id=request.user.id
        ).exists()


class IsTaskCreatorOrBoardOwner(
    BasePermission
):

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        return (
            obj.creator == request.user
            or obj.board.owner == request.user
        )


class IsCommentAuthor(BasePermission):

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        return obj.author == request.user
