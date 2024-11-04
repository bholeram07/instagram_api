from .models import User
from rest_framework import serializers
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.serializers import ValidationError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .tasks import send_email
from django.utils import timezone
import re
from .validators import validate_password
from .utils import *
from random import randint
from .models import OtpVerification

class SignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        style={"input_type : password"}, write_only=True
    )
    password = serializers.CharField(
      style={"input_type : password"},write_only = True
    )
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
        )
    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        
        if password != confirm_password:
            raise serializers.ValidationError("password must be equal to the confirm password")
        validate_password(password, username)

        return data

    

    def validate_username(self, data):
       
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", data):
            raise serializers.ValidationError(
                "Username should not contain any special characters."
            )
        if re.search(r"\s", data):
            raise serializers.ValidationError("Username must not contain any spaces.")
        
        return data
    
    def validate_email(self,data):
        if 'gkmit.co' in data:
            raise ValidationError("This mail refers to an organization please enter a different mail ")
        if '@gmail.com' not in data:
            raise ValidationError("Please enter a valid mail")
        
        return data
    
    
    
    def create(self, validate_data):
        validate_data.pop('confirm_password')
        user = User.objects.create(**validate_data)
        user.set_password(validate_data["password"])
        user.save()
        message = f'Hi {user.username},\n\n Welcome to our platform \nThank you for signing up!\n\nBest regards,\n@gkmit'
        subject = "Welcome Message"
        # send_email.delay(user.id,message,subject)
        return user
    

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        # Get the user by email and check OTP
        otp_record = OtpVerification.objects.filter(otp=otp, user__email=email).last()
        print(otp_record)
        if not otp_record or otp_record.otp != otp:
            raise ValidationError("Invalid or expired OTP.")
        
        
        user = otp_record.user
        print(user)
        if user.is_verified:
            return ValidationError("User Already verified")
        user.is_verified = True
        print(user.is_verified)
       
        user.save() 
        # otp_record.delete()
        
        return data

    

class SendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User not found with this email.")
        return value
    
    

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")
        

    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('bio' , 'link' , 'other_social' , 'profile_image','username')
    
    def update(self, instance, validate_data):
        username = validate_data.get('username',instance.username)
        if username != instance.username :
            now = timezone.now()
            day_last_change = (now - instance.last_username_change).days if instance.last_username_change else None
            if instance. username_change_count >3:
                if day_last_change is not None and day_last_change < 15:
                    raise ValidationError("Now You can only Change your username after 15 days")
            
            instance.username_change_count +=1
            instance.last_username_change = now
            instance.username = username
            
        instance.bio = validate_data.get('bio',instance.bio)
        instance.link = validate_data.get('link',instance.link)
        instance.other_social = validate_data.get('other_socal',instance.other_social)
        instance.image = validate_data.get('profile_image',instance.image)
        instance.save()
        return instance
    
    
    
    
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    # username = serializers.CharField()


class UpdateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate(self, data):
        new_password = data.get("new_password")
        validate_password(new_password, None)
        return data
        


class SendResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ("email",)

    def validate(self, attrs):
        email = attrs.get("email")
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("You are not registered.")
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        max_length=20, style={"input_type : password"}, write_only=True
    )
    confirm_password = serializers.CharField(
        max_length=20, style={"input_type : password"}, write_only=True
    )

    class Meta:
        fields = ("password", "confirm_password")

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")
        user_id = self.context.get("user_id")
        token = self.context.get("token")

        if new_password != confirm_password:
            raise serializers.ValidationError(
                "password does not match with the confirm password"
            )

        id = smart_str(urlsafe_base64_decode(user_id))
        user = User.objects.get(id=id)
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Token is not matched or expired")
        validate_password(new_password,None)
        user.set_password(new_password)
        user.save()
        return attrs
    
    