from .models import User
from rest_framework import serializers
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import *
import re
from .validators import validate_password


class SignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        style={"input_type : password"}, write_only=True
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

    def create(self, validate_data):
        validate_data.pop('confirm_password')

        user = User.objects.create(**validate_data)
        
        user.set_password(validate_data["password"])
        user.save()
        self.send_confirmation_email(user)
        return user
    
    def send_confirmation_email(self, user):
        message = f'Hi {user.username},\n\n Welcome to our platform \nThank you for signing up!\n\nBest regards,\n@gkmit'
        email_data = {
                "subject": "Welcome message",
                "body": message,
                "to_email": user.email,
            }
        Util.send_mail(email_data)



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


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
