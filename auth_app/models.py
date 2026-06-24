"""
User model configuration for the authentication application.

This module contains the custom User model and UserManager.
The user authentication is based on email instead of username.
"""
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)

from django.db import models

class UserManager(BaseUserManager):
    """
    Custom manager for creating User instances.

    Provides methods for creating normal users and superusers
    using email authentication instead of usernames.
    """
    def create_user(
        self,
        email,
        password=None,
        **extra_fields
    ):
        """
        Create and save a normal user.
        Args: email: User email address.
              password: User password.
              extra_fields: Additional user attributes.
        Returns: User: Created user instance.
        Raises: ValueError: If no email address is provided.
        """
        if not email:
            raise ValueError(
                "Email is required"
            )

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)

        user.save(
            using=self._db
        )

        return user

    def create_superuser(
        self,
        email,
        password=None,
        **extra_fields
    ):
        """
        Create and save a superuser.
        Automatically sets staff, superuser and active permissions.
        Args: email: Superuser email address.
              password: Superuser password.
              extra_fields: Additional user attributes.
        Returns: User: Created superuser instance.
        Raises: ValueError: If required admin permissions are missing.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True"
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True"
            )

        return self.create_user(
            email,
            password,
            **extra_fields
        )


class User(AbstractUser):
    """
    Custom User model.
    Replaces the default Django username authentication
    with email-based authentication.
    Attributes:fullname: Full name of the user.
               email: Unique email address used for login.
    """
    username = None
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        """
        Return string representation of the user.
        Returns: str: User email address.
        """
        return self.email