from rest_framework.permissions import BasePermission
from rest_framework.permissions import BasePermission
from .models import User


class IsUserVerified(BasePermission):
    message = "Your account is not verified. Please verify your account."

    def has_permission(self, request, view):
        email = request.data.get("email") or request.query_params.get("email")

        if email:
            try:
                user = User.objects.get(email=email)
                return user.is_verified
            except User.DoesNotExist:
                return False

        return False
