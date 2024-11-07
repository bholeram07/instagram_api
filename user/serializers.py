from .models import User
from rest_framework import serializers
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import *


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
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        username = data.get("username")
        if password != confirm_password:
            raise serializers.ValidationError(
                "Password does not match with confirm password"
            )
        common_password = ["12345678"]
        if len(password) < 7: #add special symbolize
            raise serializers.ValidationError(
                "The length of the password must be more than 7"
            )
        if password in common_password:
            raise serializers.ValidationError(
                "The Password is too common please choose different password"
            )
        if password == username:
            raise serializers.ValidationError("Password not be username")
        return super().validate(data)

    def validate_username(self, data):
        special_char = "!@#$%^&*()_+"
        if any(char in special_char for char in data):
            raise serializers.ValidationError(
                "Username should not contain any special characters."
            )
        return data

    def create(self, validate_data):
        user = User.objects.create(
            username=validate_data["username"],
            first_name=validate_data["first_name"],
            last_name=validate_data["last_name"],
            email=validate_data["email"],
        )
        user.set_password(validate_data["password"])
        user.save()
        return user


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


class SendResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ("email",)

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user_id = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = "http://localhost:3000/api/user/reset/" + user_id + "/" + token
            print(link)
            body = " This is your link to reset password " + link

            data = {
                "subject": "Reset Your Password",
                "body": body,
                "to_email": user.email,
            }
            print("outside function")
            Util.send_mail(data)
            return attrs

        else:
            return serializers.ValidationError("You are not Registered")


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=20, style={"input_type : password"}, write_only=True
    )
    confirm_password = serializers.CharField(
        max_length=20, style={"input_type : password"}, write_only=True
    )

    class Meta:
        fields = ("password", "confirm_password")

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        user_id = self.context.get("user_id")
        token = self.context.get("token")

        if password != confirm_password:
            raise serializers.ValidationError(
                "password does not match with the confirm password"
            )

        id = smart_str(urlsafe_base64_decode(user_id))
        user = User.objects.get(id=id)
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Token is noe matched or expired")
        user.set_password(password)
        user.save()
        return attrs
