from .models import User
from rest_framework import serializers
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
# from rest_framework.serializers import ValidationError
from rest_framework.exceptions import ValidationError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .tasks import send_welcome_email
from django.utils import timezone
import re
from .validators import validate_password
from .utils import *
from random import randint
from .models import OtpVerification,Follow
from post_app.models import Post




class SignupSerializer(serializers.ModelSerializer):
    """
    _summary_
     Serializer for signup the user it takes the user's detail and valdiate the differrent paramenters 
     

    Args:
       serializers (ModelSerializer): Django Rest Framework's model serializer
            for defining fields and validating data.

    Raises:
         serializers.ValidationError: Raised if a field contains invalid data
            or does not meet the required criteria.
        serializers.ValidationError: Raised if the provided username is already
            taken by another user.
        serializers.ValidationError: raised if the username is not provided.
        ValidationError: Raised if the password is not in correct format.
        ValidationError: Raised username is not in correct format

    Returns:
        _dict_ : The username ,firstname,lastname,email and password
    """

    confirm_password = serializers.CharField(
        style={"input_type : password"}, write_only=True
    )

    password = serializers.CharField(style={"input_type : password"}, write_only=True)

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
        email = data.get("email")
        confirm_password = data.get("confirm_password")
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"datail" : "This email is already registered"})
        
        if User.objects.filter(username=username).exists():
            raise serializer.ValidationError({"detail" : "Username is already registered"})

        if password != confirm_password:
            raise ValidationError(
                "password must be equal to the confirm password"
            )
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
        validate_data.pop("confirm_password")
        user = User.objects.create(**validate_data)
        user.set_password(validate_data["password"])
        user.save()
        send_welcome_email.delay(user.id)
        return user


class VerifyOtpSerializer(serializers.Serializer):
    """
    _summary_
    serialzer for verify the otp that send to the email of the user
    it takes the otp and return the verified user
    

    Args:
        otp(str): The otp send at the mail of the user
        email(str) : The email of the user
    Raises:
        ValidationError: Raised if the otp provided by user is not matched with the sent otp
        ValidationError: Raised if the otp provided is expired or invalid

    Returns:
        bool : verified user
    """

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get("email")
        otp = data.get("otp")

       
        otp_record = OtpVerification.objects.filter(otp=otp, user__email=email).last()
        print(otp_record)
        if not otp_record or otp_record.otp != otp:
            raise ValidationError("Invalid or expired OTP.")

        user = otp_record.user
        if user.is_verified==True:
            raise ValidationError("User Already verified")
        
        user.is_verified = True
        print(user.is_verified)

        user.save()

        return data


class SendOtpSerializer(serializers.Serializer):
    """
    _summary_

    Serializer for handling the email of the registered user,allowing to send the
    random 6 digits otp to the provided registered mail of the user


    Args:
        email (str): email of the registered user

    Raises:
        serializers.ValidationError: _description_

    Returns:
        str: return the validate email of the user
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User not found with this email.")
        return value

class ProfileSerializer(serializers.ModelSerializer):
    """
    _summary_

    Serializer for handling user profile data, allowing users to update
    their profile with bio, social links, profile image, and username.
    Performs validation on input fields and raises errors as necessary.

    Args:
        serializers (ModelSerializer): Django Rest Framework's model serializer
            for defining fields and validating data.

    Raises:
        serializers.ValidationError: Raised if a field contains invalid data
            or does not meet the required criteria.
        serializers.ValidationError: Raised if the provided username is already
            taken by another user.
        serializers.ValidationError: Raised if the profile image format is
            unsupported or exceeds the allowed file size.
        ValidationError: Raised if the social media links contain invalid URLs.
        ValidationError: Raised if the bio field exceeds the maximum allowed length.

    Returns:
        dict: The validated and serialized user profile data, including id, bio,
            other_social, profile_image, and username fields.
    """
    posts = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ("id", "bio", "other_social", "profile_image", "username",'posts','is_private','followers','following')
        
    def get_posts(self, obj):
        return Post.objects.filter(user=obj, is_deleted=False).count()  
    
    def get_followers(self, obj):
        return obj.following.count()

    def get_following(self, obj):
        return obj.follower.count()

    def update(self, instance, validate_data):
        if not validate_data:
            raise ValidationError({"error" : "provide data to update"})
        username = validate_data.get("username", instance.username)
        if username != instance.username:
            now = timezone.now()
            day_last_change = (
                (now - instance.last_username_change).days
                if instance.last_username_change
                else None
            )
            if instance.username_change_count > 3:
                if day_last_change is not None and day_last_change < 15:
                    raise ValidationError(
                        "Now You can only Change your username after 15 days"
                    )

            instance.username_change_count += 1
            instance.last_username_change = now
            instance.username = username

        instance.bio = validate_data.get("bio", instance.bio)
        instance.other_social = validate_data.get("other_social", instance.other_social)
        instance.profile_image = validate_data.get(
            "profile_image", instance.profile_image
        )
        instance.save()

        return instance


class LoginSerializer(serializers.Serializer):
    """
    _summary_

    This serializer handles user authentication by validating the provided
    email and password. The email must be a valid email format, and the
    password is a plain text string.

    Args:
        email(str) : email of the user
        password(str) : password of the user

    Raises:
        serializers.ValidationError: if email format is encorrect


    """

    email = serializers.EmailField()
    password = serializers.CharField()


class UpdateSerializer(serializers.Serializer):
    """
    _summary_

    This serializer handles the password updation by validating the
    authenticated user.he email must be a valid email format and
    The password must be a strong and valid text string

    Args:
        email(str) : The email address of the user
        new_password(str) : The new password of the user
        confirm_password (str) : The confirm password of the user

    Returns:
        retuens the validate data email and password of the user
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        new_password = data.get("new_password")
        current_password = data.get("current_password")
        user = self.context['request'].user
        validate_password(new_password, None)
        if not user.check_password(current_password):
            raise ValidationError("Password is not valid")
        if new_password == current_password :
            raise ValidationError("The current password and new password can't be same")
        return data


class SendResetPasswordEmailSerializer(serializers.Serializer):
    """
    _summary_

    Serializer for sending the reset password link to the user's email. validate
    the email of the user


    Args:
        email (str): email of the user

    Raises:
        serializers.ValidationError: Raised if the email is not registered
        serializers.ValidationError: Raised if the email is not in correct format

    Returns:
        str : return the validate email of type str
    """

    email = serializers.EmailField()

    class Meta:
        fields = ("email",)

    def validate(self, attrs):
        email = attrs.get("email")
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("You are not registered.")
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """
    _summary_

    Serializer for reset the password of the registered user


    Args:
        new_password (str): new_password of the user
        confirm_password(str) : confirm password of the user

    Raises:
        serializers.ValidationError: _
        serializers.ValidationError: _description_

    Returns:
        _type_: _description_
    """

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
        validate_password(new_password, None)
        user.set_password(new_password)
        user.save()
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer()  # Use the nested UserSerializer for detailed info
    following = UserSerializer()

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at', 'status']
