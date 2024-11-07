from django.urls import path
from django.contrib import admin
from .views import *

urlpatterns = [
    path("signup/", Signup.as_view(), name="signup-user"),
    path("profile/", UserProfile.as_view(), name="user-profile"),
    path("send-otp/", SendOtp.as_view(), name="send-otp"),
    path("verify/", VerifyOtp.as_view(), name="Verify Otp"),
    path("login/", Login.as_view(), name="login-user"),
    path("update-password/", UpdatePassword.as_view(), name="update-password"),
    path(
        "reset-password/send-email/",
        SendResetPasswordEmail.as_view(),
        name="reset-password-send-email",
    ),
    path(
        "password/reset/<user_id>/<token>/",
        ResetPassword().as_view(),
        name="reset-password",
    ),
    path(
        "friends/requests/",
        FriendRequestView.as_view({"post": "create"}),
        name="send-request",
    ),
    path(
        "friends/requests/<int:pk>/",
        FriendRequestView.as_view({"put": "update"}),
        name="manage-request",
    ),
    path("feed/", FeedView.as_view({"get": "list"}), name="user-feed"),
]
