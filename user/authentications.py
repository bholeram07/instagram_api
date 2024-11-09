from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
User = get_user_model()


def get_token_for_user(user):
    token = RefreshToken.for_user(user)
    token['last_password_change'] = user.last_password_change.timestamp() if user.last_password_change else 0
    return token



class CustomJwtAuthentication(JWTAuthentication):
    def get_user(self,validated_token):
        user = super().get_user(validated_token)
        token_timestamp = validated_token.get('last_password_change',0)
        if user is not None:
            last_password_change = timezone.datetime.fromtimestamp(token_timestamp)
            last_password_change = timezone.make_aware(
                timezone.datetime.fromtimestamp(token_timestamp),
                timezone.get_current_timezone()
            )
            if user.last_password_change and user.last_password_change.tzinfo is None:
                user.last_password_change = timezone.make_aware(user.last_password_change, timezone.get_current_timezone())
            if last_password_change < user.last_password_change:
                raise AuthenticationFailed("You have to login first ")
        
        return user
       