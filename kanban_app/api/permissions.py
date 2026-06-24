"""
Permission classes for the Kanban application.

This module contains custom Django REST Framework permissions.
These permissions control access to boards, tasks and comments
based on the relationship between users and objects.
"""

from rest_framework.permissions import BasePermission

class IsBoardOwner(BasePermission):
    """
    Permission that allows access only to the owner of a board.
    A user must be the owner of the board object to perform
    the requested action.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the current user owns the board.
        Args: request: The current HTTP request.
              view: The API view handling the request.
              obj: The board object being accessed.
        Returns: bool: True if the user is the board owner,
                 otherwise False.
        """
        return obj.owner == request.user


class IsBoardMemberOrOwner(BasePermission):
    """
    Permission that allows access to board owners and members.
    A user can access a board if they either own it
    or are added as a member.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the current user is owner or member of the board.
        Args: request: The current HTTP request.
              view: The API view handling the request.
              obj: The board object being accessed.
        Returns: bool: True if user is owner or member,
                 otherwise False.
        """
        return (
            obj.owner == request.user
            or obj.members.filter(id=request.user.id).exists()
        )


class IsTaskBoardMember(BasePermission):
    """
    Permission that allows access to tasks of a board member.
    The user must be a member of the board that contains the task.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        """
        Check if the user belongs to the task's board.
        Args: request: The current HTTP request.
              view: The API view handling the request.
              obj: The task object being accessed.
        Returns: bool: True if user is a board member,
                 otherwise False.
        """
        return obj.board.members.filter(
            id=request.user.id
        ).exists()


class IsTaskCreatorOrBoardOwner(BasePermission):
    """
    Permission that allows access to task creators
    or the owner of the related board.
    A task can be modified by its creator or by the board owner.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        """
        Check if the user created the task
        or owns the related board.
        Args: request: The current HTTP request.
              view: The API view handling the request.
              obj: The task object being accessed.
        Returns: bool: True if user is creator or board owner,
                 otherwise False.
        """
        return (
            obj.creator == request.user
            or obj.board.owner == request.user
        )


class IsCommentAuthor(BasePermission):
    """
    Permission that allows access only to comment authors.
    A user can edit or delete a comment only if they created it.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        """
        Check if the current user is the comment author.
        Args: request: The current HTTP request.
              view: The API view handling the request.
              obj: The comment object being accessed.
        Returns: bool: True if user is the author, otherwise False.
        """
        return obj.author == request.user