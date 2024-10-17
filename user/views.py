from django.shortcuts import render
from django.shortcuts import render
from .models import User
from rest_framework.decorators import permission_classes
from rest_framework.decorators import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.response import Response
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
        print(user)
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
                        ],  # Access token expiration timestamp
                        "refresh_token_expiration": refresh.payload["exp"],
                    }
                )
            else:
                return Response(
                    {
                        "errors": {
                            "non_field_errors": ["Email or Password is not Valid"]
                        }
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
    def post(self, request):
        serializer = UpdateSerializer(data=request.data)
        user = request.user
        
        if serializer.is_valid():
            if user.check_password(serializer.validated_data["current_password"]):
                user.set_password(serializer.validated_data["new_password"])
                user.save()
                return Response(
                    {"message": "password updated successfully"},
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                return Response(
                    {"error": "password is incorrect"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {"error": serializer.errors}, status=status.HTTP_401_UNAUTHORIZED
        )


class SendResetPasswordEmail(APIView):
    def post(self, request):
        serializer = SendResetPasswordEmailSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"message": "Link Send Successfully please Check your Email"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )


class ResetPassword(APIView):
    def post(self, request, user_id, token):
        serializer = ResetPasswordSerializer(
            data=request.data, context={"user_id": user_id, "token": token}
        )
        if serializer.is_valid():
            return Response(
                {"message": "Password Updated Successfully"}, status=status.HTTP_200_OK
            )

        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

# Create your views here.
