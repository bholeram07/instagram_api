from django.urls import path
from django.contrib import admin
from .views import *

urlpatterns = [
    path('signup/', Signup.as_view()),
    path('get/', UserProfile.as_view()),
    path('login/', Login.as_view()),
    path('update-password/', UpdatePassword.as_view()),
    path('reset-password/',SendResetPasswordEmail.as_view()),
    path('reset-password/<user_id>/<token>/', ResetPassword().as_view()),
]
