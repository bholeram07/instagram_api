from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS
from user.models import User

class IsOwnerOrCommentAuthor(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.post.user == request.user or obj.user == request.user

 # Assuming Post and Comment are related to User


class IsOwnerOrFollower(BasePermission):
    """
    Custom permission to only allow the owner of a private account or their followers
    to access their posts and comments.
    """
    def has_permission(self, request, view):
        user = request.user
        user_id = view.kwargs.get('user_id')  # Get the user_id from the URL kwargs (if available)

       
        if not user.is_private:
            return True  # Public accounts allow all requests

        # Case 2: If the account is private, only followers or the user themselves can access posts/comments
        if user.is_private:
            # Check if the user is trying to access their own content or if they are a follower of the user
            if 'post_id' in view.kwargs:
                post_id = view.kwargs.get('post_id')
                try:
                    post = Post.objects.get(id=post_id)
                    # Check if the current user is the owner of the post or a follower of the post's owner
                    if post.owner == user or Follow.objects.filter(follower=request.user, following=post.owner, status="accepted").exists():
                        return True
                except Post.DoesNotExist:
                    return False

            elif 'comment_id' in view.kwargs:
                comment_id = view.kwargs.get('comment_id')
                try:
                    comment = Comment.objects.get(id=comment_id)
                    # Check if the current user is the owner of the comment or a follower of the comment's author
                    if comment.author == user or Follow.objects.filter(follower=request.user, following=comment.author, status="accepted").exists():
                        return True
                except Comment.DoesNotExist:
                    return False

        # Default Denial: If the account is private and the user is not a follower, deny access
        return False
