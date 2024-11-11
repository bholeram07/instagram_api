from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.decorators import api_view, permission_classes
from .models import Post, Comment, Like
from user.models import User
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .paginations import CustomPagination
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.response import Response
from .permissions import IsOwnerOrCommentAuthor
from rest_framework import status
from .response import response
from django.utils import timezone


class PostViewSet(ModelViewSet):
    queryset = Post.objects.filter(is_deleted=False).order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, user_id=None):
        if user_id:
            post = Post.objects.filter(user_id=user_id, is_deleted=False).order_by(
                "-created_at"
            )
            if not post.exists():
                return Response({"Message": "post not exists for this user"},status= status.HTTP_204_NO_CONTENT)
        else:
            user = request.user
            post = Post.objects.filter(user_id=user.id, is_deleted=False).order_by(
                "-created_at"
            )
            if not post.exists():
                return Response({"Message": "post not exists for this user"},status = status.HTTP_204_NO_CONTENT)
        paginator = CustomPagination(request, post, page_size=5)
        paginated_data = paginator.paginated_data
        serializer = self.get_serializer(paginated_data, many=True)
        return paginator.get_paginated_response({"data": serializer.data})

    def destroy(self, request, pk=None):
        post = get_object_or_404(Post, id=pk, user=request.user, is_deleted=False)
        if post.user != request.user:
            return response(403, error="permission Denied", message="Not authorized")
        post.is_deleted = True
        post.save()
        serializers = PostSerializer(instance=post)
        return response(200, message="Post Deleted", data=serializers.data)

    def update(self, request, pk=None):
        post = get_object_or_404(Post, id=pk, user=request.user, is_deleted=False)
        if post.user != request.user:
            raise PermissionDenied("Not authorized to update this post")

        serializer = self.get_serializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Post updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavedPostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        saved_posts = SavedPost.objects.filter(user=user).select_related("post")
        serializer = SavedPostSerializer(saved_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if SavedPost.objects.filter(user=user, post=post).exists():
            return Response(
                {"detail": "You have already saved this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        saved_post = SavedPost.objects.create(user=user, post=post)
        serializer = SavedPostSerializer(saved_post)

        return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        saved_post = SavedPost.objects.filter(user=user, post=post).first()
        if not saved_post:
            return Response(
                {"detail": "This post is not in your saved list."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        saved_post.delete()
        return Response(
            {"detail": "Post unsaved successfully."}, status=status.HTTP_204_NO_CONTENT
        )


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.filter(is_deleted=False, parent=None).order_by(
        "-created_at"
    )
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrCommentAuthor]

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        if post_id:
            return Comment.objects.filter(
                post_id=post_id, parent=None, is_deleted=False
            ).order_by("-created_at")
        return Comment.objects.filter(is_deleted=False, parent=None)

    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        print(post_id)
        post = get_object_or_404(Post, id=post_id)

        parent_id = self.request.data.get("parent")
        parent_id = self.request.query_params.get("parent")
        print(f"Request Data: {self.request.data}")
        
        parent_comment = None
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id, post_id=post_id)
        serializer.save(post=post, user=self.request.user, parent=parent_comment)

    def destroy(self, request, pk=None):
        comment = get_object_or_404(Comment, id=pk, user=request.user, is_deleted=False)
        comment.is_deleted = True
        comment.save()
        serializers = CommentSerializer(instance=comment)
        return response(200, message="Comment Deleted", data=serializers.data)

    def list(self, request, post_id=None):
        if not post_id:
            return Response({"message": "Please Provide Post id"})
        comment = Comment.objects.filter(post_id=post_id, is_deleted=False).order_by(
            "-created_at"
        )
        if not comment.exists():
            return Response({"Message": "comment not exists for this post"},status=status.HTTP_204_NO_CONTENT)
        paginator = CustomPagination(request, comment, page_size=5)
        paginated_data = paginator.paginated_data
        serializer = self.get_serializer(paginated_data, many=True)
        return paginator.get_paginated_response({"data": serializer.data})

    def update(self, request, pk=None):

        comment = get_object_or_404(Comment, id=pk, is_deleted=False)
        serializer = self.get_serializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if Like.objects.filter(post=post, user=request.user).exists():
            raise ValidationError("You have already liked this post.")
        Like.objects.create(post=post, user=request.user)
        likes_count = Like.objects.filter(post=post).count()
        serializers = PostSerializer(instance=post)

        data = (serializers.data,)
        message = f"Post liked successfully, Likes = {likes_count}"
        return response(201, data, message, None)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        if Like.objects.filter(post=post).exists():
            Like.objects.filter(post=post).delete()
            likes_count = Like.objects.filter(post=post).count
            serializers = PostSerializer(instance=post)
            message = ("Post unliked",)
            data = serializers.data
            return response(200, data, message, None)

        else:
            return response(
                404, data=None, message="Not found any likes of you", error="Not found"
            )

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        Like.objects.filter(post=post).count()
        serializers = PostSerializer(instance=post)
        return Response(
            {"Post": serializers.data, "Likes": Like.objects.filter(post=post).count()}
        )
