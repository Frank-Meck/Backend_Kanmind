from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None

    fullname = models.CharField(max_length=255, verbose_name="Full Name",)
    email = models.EmailField(unique=True, verbose_name="Email Address",)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["id"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email
