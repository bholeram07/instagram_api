from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_user_model
from rest_framework.authentication import JWTAuthentication
from django.shortcuts import timezone

User = get_user_model


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
            if last_password_change < user.last_password_change:

                raise Exception("Your password has changed since this token was issued.")
        
        return user
       
    


