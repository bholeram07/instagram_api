from django.urls import path
from django.contrib import admin
from .views import *

urlpatterns = [
    path("signup/", Signup.as_view(), name="signup-user"),
    path("get-profile/", UserProfile.as_view(), name="user-profile"),
    path("send-otp/",SendOtp.as_view(),name="send-otp"),
    path("verify/",VerifyOtp.as_view(),name = "Verify Otp"),
    path("login/", Login.as_view(), name="login-user"),
    path("update-password/", UpdatePassword.as_view(), name="update-password"),
    path("reset-password/send-email/", SendResetPasswordEmail.as_view(),name="reset-password-send-email",),
    path("password/reset/<user_id>/<token>/",ResetPassword().as_view(), name="reset-password",
    ),
]
