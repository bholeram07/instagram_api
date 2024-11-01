
from .models import User
from rest_framework.decorators import APIView
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.response import Response
from .authentications import get_token_for_user
from .permissions import IsUserVerified
from django.utils import timezone
# from .send_mail import send_confirmation_email
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .tasks import *


class Signup(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"user": serializer.data,
                 "message" : "User Signup Successfully"
                 }, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

class VerifyOtp(APIView):
    def post(self,request):
        serializer = VerifyOtpSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Message" :"OTP verification Successfull",
            },status=200)
        return Response({
            'error' : serializer.errors, 
        },status=status.HTTP_202_ACCEPTED)

class UserProfile(APIView):
    permission_classes =[IsAuthenticated],[IsUserVerified]
    def post(self,request):
        user = request.user
        if user:
            serializer = ProfileSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "Profile" :serializer.data,
                    "message" : "profile created"
                } ,status= status.HTTP_201_CREATED)
        return Response(
            {"error": serializers.errors}, status=status.HTTP_400_BAD_REQUEST
        )
    def get(self,request):
        user = request.user
        if user:
            serializer = ProfileSerializer(data = request.data)
            return Response({"user": serializers.data}, status=status.HTTP_200_OK)
        return Response(
            {"error": serializers.errors}, status=status.HTTP_400_BAD_REQUEST
        )    
    
    def put(self,request):
        user = request.user
        if user:
            serializer = ProfileSerializer(data = request.data)
            if serializer.is_valid():
                return Response({
                    "Updated-Profile" : serializer.data,
                    "message" : "Profile Updated",
                },status=status.HTTP_202_ACCEPTED)
            

class Login(APIView):
    def post(self, request):
        serializers = LoginSerializer(data=request.data)
        if serializers.is_valid():
            email = serializers.validated_data["email"]
            username = serializers.validated_data["username"] 
            password = serializers.validated_data["password"]
            if email:
                user = authenticate(email=email, password=password)
            elif username:
                user = authenticate(email = username, password=password)
            
            if user:
                token = get_token_for_user(user)
                return Response(
                    {
                        "refresh": str(token),
                        "access": str(token.access_token),
                        "access_token_expiration": token.access_token.payload[
                            "exp"
                        ],  
                        "refresh_token_expiration": token.payload["exp"],
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
                user.set_password(serializer.validated_data["new_password"])
                user.last_password_change = timezone.now()  
                user.save()

                return Response(
                    {"message": "Password updated successfully"},
                    status=status.HTTP_202_ACCEPTED
                )
            else:
                return Response(
                    {"error": "Current password is incorrect."},
                    status=status.HTTP_400_BAD_REQUEST
                )
       
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


class Logout(APIView):
    def post(self,request):
        user = request.user
        if user:
             user.last_password_change = timezone.now() 
             user.save()
             return Response({
                 'message' :"Successfully Loged out"

             })
             
        else :
            return Response({
                "message" : "You have to login first for the logout"
            })