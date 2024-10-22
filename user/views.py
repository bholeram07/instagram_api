from django.shortcuts import render
from django.shortcuts import render
from .models import User
from rest_framework.decorators import permission_classes
from rest_framework.decorators import APIView
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import *
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.response import Response
# from .send_mail import send_confirmation_email
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    SignupSerializer,
    UserSerializer,
    LoginSerializer,
    UpdateSerializer,
    SendResetPasswordEmailSerializer,
    ResetPasswordSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from .models import BlacklistedToken


class Signup(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "user created successfully"}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


class UserProfile(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if user:
            serializers = UserSerializer(user)
            return Response({"user": serializers.data}, status=status.HTTP_200_OK)
        return Response(
            {"error": serializers.errors}, status=status.HTTP_400_BAD_REQUEST
        )


class Login(APIView):
    def post(self, request):
        serializers = LoginSerializer(data=request.data)
        if serializers.is_valid():
            email = serializers.validated_data["email"]
            password = serializers.validated_data["password"]
            user = authenticate(email=email, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "access_token_expiration": refresh.access_token.payload[
                            "exp"
                        ],  
                        "refresh_token_expiration": refresh.payload["exp"],
                    }
                )
            else:
                return Response(
                    {
                        
                        "error" :   "Email or Password is not Valid"
                        
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response(
            {
                "errors": serializers.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )




class UpdatePassword(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateSerializer(data=request.data)
        user = request.user

        if serializer.is_valid():
            if user.check_password(serializer.validated_data["current_password"]):
                # Set the new password
                user.set_password(serializer.validated_data["new_password"])
                user.save()
                # subject = 'Regarding Update Password',
                # body = "Your Password has been updated ",
                # send_confirmation_email(user,body,subject)

                # Blacklist the access token
                try:
                    access_token = request.headers.get('Authorization').split(' ')[1]
                    if access_token:
                        BlacklistedToken.objects.create(token=access_token)#token authentication
                    else:
                        return Response(
                            {"error": "Access token not provided."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except Exception as e:
                    return Response(
                        {"error": "Please Login again with new password "},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Return success response
                return Response(
                    {"message": "Password updated successfully"},
                    status=status.HTTP_202_ACCEPTED
                )
            else:
                # Invalid current password
                return Response(
                    {"error": "Current password is incorrect."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        # Invalid serializer data
        return Response(
            {"error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class SendResetPasswordEmail(APIView):
    def post(self, request):
        serializer = SendResetPasswordEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            user_id = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_link = f"{request.scheme}://{request.get_host()}/user/password/reset/{user_id}/{token}"
            body = f"This is your link to reset password: {reset_link}"
            subject= "Reset Your Password",
            # send_confirmation_email(user,body,subject)
            return Response({"message": "Password reset link sent successfully."}, status=status.HTTP_200_OK) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):
    def post(self, request, user_id, token):
        serializer = ResetPasswordSerializer(
            data=request.data, context={"user_id": user_id, "token": token}
        )
        if serializer.is_valid():
            return Response(
                {"message": "Password Reset Successfully"}, status=status.HTTP_200_OK
            )
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )


