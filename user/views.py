
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
from .serializers import *
from .tasks import *
from .models import OtpVerification
from .generate_otp import generate_otp
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from post_app.serializers import PostSerializer

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


class FreindRequestView(ModelViewSet):
    queryset = FreindRequest.objects.all()
    serializer_class = FreindRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self,request ,*args ,**kwargs):
        data = {'sender' : request.user.id, 'reciever' : request.data.get('reciever')}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    
    def update(self,request,pk=None):
        freind_request = get_object_or_404(FreindRequest,id = pk ,reciever = request.user)
        action = request.data.get('action')
        
        if action == 'accept':
            freind_request.accept()
        
        elif action == 'reject':
            freind_request.reject()
            
        
        else:
            return Response({'Message' : 'Invalid Action'},status=status.HTTP_400_BAD_REQUEST)
        
        
        return Response(FreindRequestSerializer(freind_request).data,status=status.HTTP_202_ACCEPTED)
    
    

class FeedView(ReadOnlyModelViewSet):
    serializer_class = FreindshipSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self ,*argsg,**kwargs):
        user = request.user
        friends = Friendship.objects.filter(models.Q(user1=user) | models.Q(user2=user))
        
        # Retrieve posts only from friends
        friend_posts = Post.objects.filter(user__in=[friend.user2 for friend in friends if friend.user1 == user] + [friend.user1 for friend in friends if friend.user2 == user])
        serializer = PostSerializer(friend_posts, many =True,context ={'request':request})
        return Response(serializer.data)