from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.

    Handles user creation using email as the unique identifier
    instead of username.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user.

        Args:
            email (str): User email address.
            password (str): Plain text password.
            **extra_fields: Additional user fields.

        Returns:
            User: Created user instance.

        Raises:
            ValueError: If email is not provided.
        """
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with admin permissions.

        Args:
            email (str): Superuser email address.
            password (str): Plain text password.
            **extra_fields: Additional user fields.

        Returns:
            User: Created superuser instance.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model that uses email as the unique identifier.

    Replaces username, first_name and last_name with a single
    fullname field.
    """

    username = None
    first_name = None
    last_name = None

    fullname = models.CharField(
        max_length=255,
        verbose_name="Full Name",
    )

    email = models.EmailField(
        unique=True,
        verbose_name="Email Address",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        """
        Meta configuration for User model.

        Defines default ordering and human-readable names.
        """
        ordering = ["id"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        """
        Return string representation of the user.

        Returns:
            str: Email of the user.
        """
        return self.email