from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from .models import Post, Comment, Like
from .serializers import (
    PostSerializer,
    CommentSerializer,
    LikeSerializer,
    GetPostSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .paginations import CustomPagination


class PostView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = [CustomPagination]

    def post(self, request):
        serializer = PostSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {"message": "Post Created Successfully"}, status=status.HTTP_201_CREATED
            )

        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request):
        post = Post.objects.filter(user=request.user)
        print(request.user)
        if post:
            serializers = GetPostSerializer(post, many=True)
            return Response({"user": serializers.data}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Not any post found of this User"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, post_id):
        post = Post.objects.get(id=post_id)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "post Updated Successfully"},
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(
            {"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, post_id):

        try:
            post = Post.objects.get(id=post_id)
        except:
            return Response(
                {"error": "Post Does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        post.delete()
        return Response(
            {"message": "Post Deleted Successfully"}, status=status.HTTP_200_OK
        )


class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = [CustomPagination]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id) 
            data = request.data.copy()
            data["post"] = post_id  
            serializer = CommentSerializer(
                data=request.data, context={"request": request, "post": post}
            )

            if serializer.is_valid():
                serializer.save()  
                return Response(
                    {"data": serializer.data}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )

        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            comments = Comment.objects.filter(post=post)  
            serializer = CommentSerializer(comments, many=True)

            return Response({"data": serializer.data}, status=status.HTTP_200_OK)

        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, comment_id):
        comment = Comment.objects.filter(id=comment_id)
        if comment == None:
            return Response(
                {"message": "comment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        comment.delete()
        return Response(
            {"message": "Comment Deleted Successfully"}, status=status.HTTP_200_OK
        )

    def put(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Comment updated Successfully"}, status=status.HTTP_200_OK
            )
        return Response(
            {
                "error": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )



class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve all Like objects
        likes = Like.objects.all()
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        # Check if the post exists
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        # Prepare data for serializer
        data = request.data.copy()  # Copy request data
        data['post'] = post.id  # Associate with the post

        # Instantiate the serializer with the request context
        serializer = LikeSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            serializer.save()  # Save the like (user will be set automatically)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






# Create your views here.
