"""
URL configuration for the authentication application.

This module defines API endpoints for user authentication,
including registration and login functionality.
"""
from django.urls import path

from .views import (
    RegisterView,
    LoginView,
)

urlpatterns = [

    path("registration/", RegisterView.as_view(),),
    path("login/", LoginView.as_view(),),
]