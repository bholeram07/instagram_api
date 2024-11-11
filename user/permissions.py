from rest_framework.permissions import BasePermission
from rest_framework.permissions import BasePermission
from .models import User

class IsUserVerified:
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if user is None or user.is_anonymous:
            email = request.data.get("email") or request.query_params.get("email")
            if email:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    return False
            else:
                return False  
        return user.is_verified



