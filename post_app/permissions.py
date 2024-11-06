from rest_framework.permissions import BasePermission

class IsOwnerOrCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.post.user == request.user:
            return True  
        return obj.user == request.user  
    

