from django.urls import path
from django.contrib import admin
from .views import *

urlpatterns = [
    path("signup/", Signup.as_view(), name="signup-user"),
    path("profile/", UserProfile.as_view(), name="user-profile"),
    path("profile/<str:user_id>/",UserProfile.as_view()),
    
    path("send-otp/", SendOtp.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOtp.as_view(), name="verify-otp"),
    path("login/", Login.as_view(), name="login"),
    path("logout/",Logout.as_view(), name= "logout"),
    path("update-password/", UpdatePassword.as_view(), name="update-password"),
    path(
        "reset-password/send-email/",
        SendResetPasswordEmail.as_view(),
        name="reset-password-send-email",
    ),
 
    path('follow/<str:user_id>/', FollowView.as_view(), name='follow'),
    path('following/<str:user_id>/',FollowingView.as_view(), name = 'following'),
    path(
        "reset-password/<str:user_id>/<str:token>/",
        ResetPassword.as_view(),
        name="reset-password",
    ),
  
    path('follow-requests/', FollowRequestListView.as_view(), name='follow-requests-list'),
    path('follow-request/<str:follow_id>/<str:action>/', FollowRequestActionView.as_view(), name='follow-request-action'),
   
]
