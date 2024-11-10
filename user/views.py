
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
from .tasks import *
from .models import OtpVerification
from .utils import generate_otp
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from post_app.serializers import PostSerializer
from post_app.models import Post

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
            
class SendOtp(APIView):
    def post(self , request):
        email = request.data.get("email")
        user = get_object_or_404(User, email= email)
        otp = generate_otp()
        message = f"Your Otp for the verification mail {otp}"
        send_email(user.id,message,"Otp for Verification")
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
    def get(self,request):
        user = request.user
        if user:
            serializer = ProfileSerializer(user)            
            return Response({"user": serializer.data}, status=status.HTTP_200_OK)
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )    
    
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
    # permission_classes = [IsUserVerified]
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
            body = f"This is your link to reset password: {reset_link}"
            subject= "Reset Your Password",
            # send_confirmation_email(user,body,subject)
            return Response({"message": "Password reset link sent successfully."}, status=status.HTTP_200_OK) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):
    def put(self, request, user_id, token):
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


class FriendRequestView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        user = request.user
        friend_requests = FriendRequest.objects.filter(receiver=user)
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return Response(serializer.data)

    def create(self, request):
        sender = request.user
        receiver_id = request.data.get('receiver_id')
        if not receiver_id:
            return Response({"error": "Receiver ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        reciever = get_object_or_404(User,id=receiver_id)
        if Friendship.objects.filter(user1=sender, user2=reciever).exists() or Friendship.objects.filter(user1=reciever, user2=sender).exists():
            return Response({"message": "You are already friends."}, status=status.HTTP_400_BAD_REQUEST)
        
        if FriendRequest.objects.filter(sender=sender, reciever=reciever, status='pending').exists():
            return Response({"message": "Request already sent"}, status=status.HTTP_400_BAD_REQUEST)

        FreindRequest.objects.create(sender=sender, reciever=receiver)
        return Response({"message": "Friend request sent successfully"}, status=status.HTTP_201_CREATED)


    def update(self, request, pk=None):
        
        friend_request = get_object_or_404(FriendRequest,pk=pk)
        if friend_request.receiver != request.user:
            return Response({"error": "Not authorized to respond to this friend request"}, status=status.HTTP_403_FORBIDDEN)
        
        action = request.data.get("action")

        if action not in ['accept', 'reject']:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        if action == "accept":
            friend_request.status = "accepted"
            friend_request.save()

            Friendship.objects.create(user1=friend_request.sender, user2=friend_request.receiver)
            return Response({"message": "Friend request accepted"}, status=status.HTTP_200_OK)
        
        elif action == "reject":
            friend_request.status = "rejected"
            friend_request.save()
            return Response({"message": "Friend request rejected"}, status=status.HTTP_200_OK)

        request.user.friends.add(friend_request.sender)
        friend_request.sender.friends.add(request.user)

        return Response({'detail': 'Friend request accepted.'}, status=status.HTTP_200_OK)
    
    

class FeedView(ReadOnlyModelViewSet):
    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self ,request,*args,**kwargs):
        user = request.user
        friends = Friendship.objects.filter(models.Q(user1=user) | models.Q(user2=user))
        
       
        friend_posts = Post.objects.filter(user__in=[friend.user2 for friend in friends if friend.user1 == user] + [friend.user1 for friend in friends if friend.user2 == user])
        serializer = PostSerializer(friend_posts, many =True,context ={'request':request})
        return Response(serializer.data)