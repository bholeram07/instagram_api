from django.urls import path
from django.contrib import admin
from .views import *

urlpatterns = [
    path("signup/", Signup.as_view(), name="signup-user"),
    path("profile/", UserProfile.as_view(), name="user-profile"),
    path("send-otp/", SendOtp.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOtp.as_view(), name="verify-otp"),
    path("login/", Login.as_view(), name="login-user"),
    path("logout/",Logout.as_view(), name= "logout-user"),
    path("update-password/", UpdatePassword.as_view(), name="update-password"),
    path(
        "reset-password/send-email/",
        SendResetPasswordEmail.as_view(),
        name="reset-password-send-email",
    ),
 
    path('follow/<str:user_id>/', FollowView.as_view(), name='follow'),
    
    path(
        "reset-password/<user_id>/<token>/",
        ResetPassword.as_view(),
        name="reset-password",
    ),
  
    path('follow-requests/', FollowRequestListView.as_view(), name='follow-requests-list'),
    path('follow-request/<int:follow_id>/<str:action>/', FollowRequestActionView.as_view(), name='follow-request-action'),
   
]
