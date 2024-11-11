
from .models import *
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
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import *
from .tasks import send_otp_email,send_reset_password_email
from .models import OtpVerification
from .utils import generate_otp
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from post_app.serializers import PostSerializer
from post_app.models import Post
from rest_framework.permissions import AllowAny
OTP_LIMIT = 5 
OTP_TIME_LIMIT = timedelta(hours=1)  


class Signup(APIView):
    permission_classes = [AllowAny]
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
            
class SendOtp(APIView):
    def post(self , request):
        email = request.data.get("email")
        user = get_object_or_404(User, email= email)
        otp = generate_otp()
        recent_otps = OtpVerification.objects.filter(
            user = user,
            created_at__gte=timezone.now() - OTP_TIME_LIMIT
        )
        if recent_otps.count() >= OTP_LIMIT:
            return Response(
                {"message": "OTP request limit reached. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
        )
        send_otp_email.delay(user.id , otp)
        print(otp)
        OtpVerification.objects.create(user=user, otp=otp)
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
    
    
class VerifyOtp(APIView):
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            
 
class UserProfile(APIView):
    permission_classes =[IsAuthenticated]
    def get(self,request,user_id = None):
        if not user_id:
            user = request.user
            if user:
                serializer = ProfileSerializer(user)            
                return Response({"user": serializer.data}, status=status.HTTP_200_OK)
            return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )   
        else:
            user = User.objects.get(id=user_id)
            serializer = ProfileSerializer(user)
            return Response(serializer.data)
 
    
    def put(self,request):
        user = request.user
        if user:
            serializer = ProfileSerializer(instance=user ,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "Updated-Profile" : serializer.data,
                    "message" : "Profile Updated",
                },status=status.HTTP_202_ACCEPTED)
            return Response({
                "error" : serializer.errors

            })
            

class Login(APIView):
    permission_classes = [IsUserVerified]
    def post(self, request):
        serializers = LoginSerializer(data=request.data)
        if serializers.is_valid():
            email = serializers.validated_data["email"]
            password = serializers.validated_data["password"]
            user = authenticate(email=email, password=password)
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
                "Message" : "Please Verify user email"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )




class UpdatePassword(APIView):
    permission_classes = [IsAuthenticated,IsUserVerified]

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
    permission_classes = [IsUserVerified]
    def post(self, request):
        serializer = SendResetPasswordEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            user_id = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_link = f"{request.scheme}://{request.get_host()}/user/password/reset/{user_id}/{token}"
            print(reset_link)
           
            send_reset_password_email(user.id, reset_link)
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
    permission_classes = [IsAuthenticated]
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


class FollowRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        user_to_follow = get_object_or_404(User, id=user_id)
        if user_to_follow.is_private:
            follow, created = Follow.objects.get_or_create(
                user=user_to_follow,
                follower=request.user,
                defaults={'status': 'pending'}
            )
            if not created:
                return Response({"message": "Follow request already sent."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Follow request sent."}, status=status.HTTP_201_CREATED)
        else:
            follow, created = Follow.objects.get_or_create(
                user=user_to_follow,
                follower=request.user,
                defaults={'status': 'accepted'}
            )
            return Response({"message": "You are now following this user."}, status=status.HTTP_201_CREATED)


class FollowRequestUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, follow_request_id, action):
        follow_request = get_object_or_404(Follow, id=follow_request_id, user=request.user, status='pending')

        if action == 'accept':
            follow_request.status = 'accepted'
            follow_request.save()
            return Response({"message": "Follow request accepted."}, status=status.HTTP_200_OK)
        elif action == 'reject':
            follow_request.status = 'rejected'
            follow_request.save()
            return Response({"message": "Follow request rejected."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
        
        




class FollowView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
     
        followed_user = get_object_or_404(User, id=user_id)
        follower_user = request.user

        if follower_user == followed_user:
            return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

      
        if followed_user.is_private:
        
            if Follow.objects.filter(follower=follower_user, followed=followed_user).exists():
                return Response({"detail": "Follow request already sent."}, status=status.HTTP_400_BAD_REQUEST)

          
            Follow.objects.create(follower=follower_user, followed=followed_user, status='pending')
            return Response({"detail": "Follow request sent."}, status=status.HTTP_201_CREATED)
        else:
            
            if Follow.objects.filter(follower=follower_user, followed=followed_user).exists():
                return Response({"detail": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)

         
            Follow.objects.create(follower=follower_user, followed=followed_user)
            return Response({"detail": "Followed successfully."}, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        
        followed_user = get_object_or_404(User, id=user_id)
        follower_user = request.user

  
        follow = Follow.objects.filter(follower=follower_user, followed=followed_user).first()
        if not follow:
            return Response({"detail": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response({"detail": "Unfollowed successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    
class FollowRequestListView(APIView):
    def get(self, request):
        user = request.user
        follow_requests = Follow.objects.filter(user=user, status='pending')
        serializer = FollowSerializer(follow_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowRequestActionView(APIView):
    def post(self, request, follow_id, action):
        follow_request = get_object_or_404(Follow, id=follow_id, user=request.user)

        if action not in ['accept', 'reject']:
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'accept':
            follow_request.status = 'accepted'
        elif action == 'reject':
            follow_request.status = 'rejected'
        
        follow_request.save()
        return Response({"detail": f"Follow request {action}ed."}, status=status.HTTP_200_OK)