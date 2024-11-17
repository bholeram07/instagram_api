from django.urls import path
from django.contrib import admin
from .views import *
from post_app.views import PostViewSet

urlpatterns = [
    path("signup", Signup.as_view(), name="signup-user"),
    path("users/profile", UserProfile.as_view(), name="user-profile"),
    path("users/<str:user_id>/profile",UserProfile.as_view()),
    
    path("send-otp", SendOtp.as_view(), name="send-otp"),
    path("verify-otp", VerifyOtp.as_view(), name="verify-otp"),
    path("login", Login.as_view(), name="login"),
    path("logout",Logout.as_view(), name= "logout"),
    path("update-password", UpdatePassword.as_view(), name="update-password"),
    path(
        "reset-password/send-mail",
        SendResetPasswordEmail.as_view(),
        name="reset-password-send-email",
    ),
 
    path('users/<str:user_id>/follow', FollowView.as_view(), name='follow'),
   
    path('users/<uuid:user_id>/posts',PostViewSet.as_view({'get':'list'}), name="get-user-post"),
    path(
        "reset-password/<str:user_id>/<str:token>",
        ResetPassword.as_view(),
        name="reset-password",
    ),
  
    path('users/follow-requests', FollowRequestView.as_view(), name='follow-requests-list'),
    path('users/<uuid:user_id>/followers/', FollowView.as_view(), name='user-followers'),
    path('users/follow-requests/',FollowRequestView.as_view() , name = 'user-follow-requests'),
    path('users/<uuid:follow_request_id>/follow-request/<str:action>/',FollowRequestUpdateView.as_view()),
    path('users/follower/',FollowView.as_view(),name='user-follow'),
    path('users/<uuid:user_id>/follow/', FollowView.as_view(), name='user-follow'),
    path('users/<uuid:user_id>/unfollow/', FollowView.as_view(), name='user-unfollow'),
]
