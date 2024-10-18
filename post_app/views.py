from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from .models import Post, Comment, Like
from user.models import User
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .paginations import CustomPagination
from django.shortcuts import get_object_or_404


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


    def get(self, request, user_id=None):
        paginator = CustomPagination()
        if user_id is None:
            posts = Post.objects.filter(user=request.user) 
        else:
            user = get_object_or_404(User, id=user_id)  
            posts = Post.objects.filter(user=user)  
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = GetPostSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)
 

    def put(self, request, post_id):
        post = get_object_or_404(Post,id=post_id)
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
        post = get_object_or_404(Post,id=post_id)
        post.delete()
        return Response(
            {"message": "Post Deleted Successfully"}, status=status.HTTP_200_OK
        )


class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    

    def post(self, request, post_id):
            post = get_object_or_404(Post,id=post_id) 
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

    def get(self, request, post_id):
        paginator=CustomPagination()
        post = get_object_or_404(Post, id=post_id)
        comments = Comment.objects.filter(post=post)  
        paginated_posts=paginator.paginate_queryset(comments,request)
        serializer = CommentSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)
         

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        return Response(
            {"message": "Comment Deleted Successfully"}, status=status.HTTP_200_OK
        )


    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
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
        paginator = CustomPagination()
        likes = Like.objects.all()
        paginated_post = paginator.paginate_queryset(likes,request)
        serializer = GetLikeSerializer(paginated_post, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        try:
            serializer = LikeSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(post=post, user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            return Response( "already created", status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, post_id, like_id):
        post = get_object_or_404(Post, id=post_id)
        like = get_object_or_404(Like, id=like_id, post=post)

        like.delete()
        return Response({"message": "Like deleted successfully"}, status=status.HTTP_204_NO_CONTENT)