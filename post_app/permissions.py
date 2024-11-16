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
    Custom permission to allow access based on user account privacy settings.
    - Public accounts (is_private=False): Anyone can view posts and comments.
    - Private accounts (is_private=True): Only the owner and their followers can view posts and comments.
    """
    def has_permission(self, request, view):
        user = request.user
        
        # Case 1: Check if user has 'is_private' field and get privacy status
        if not hasattr(user, 'is_private'):
            return False  # User doesn't have the 'is_private' field

        # Case 2: If the account is public (is_private=False), everyone can view posts and comments
        if not user.is_private:
            return True  # Public accounts allow all requests

        # Case 3: If the account is private (is_private=True), only owner or followers can access posts/comments
        if user.is_private:
            # Determine if we are dealing with a post or a comment
            if 'post_id' in view.kwargs:
                post_id = view.kwargs.get('post_id')
                try:
                    post = Post.objects.get(id=post_id)
                    # Check if the current user is the owner or a follower of the post's owner
                    if post.owner == user or post.owner.followers.filter(id=user.id).exists():
                        return True
                except Post.DoesNotExist:
                    return False

            elif 'comment_id' in view.kwargs:
                comment_id = view.kwargs.get('comment_id')
                try:
                    comment = Comment.objects.get(id=comment_id)
                    # Check if the current user is the owner or a follower of the comment's author
                    if comment.author == user or comment.author.followers.filter(id=user.id).exists():
                        return True
                except Comment.DoesNotExist:
                    return False

        # Default Denial: If none of the above conditions are met, deny access
        return False
