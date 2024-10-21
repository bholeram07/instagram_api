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


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, user_id=None):
        if user_id :
            post = Post.objects.filter(user_id=user_id)
            if not post.exists():
                return Response({'message' : f"No any post of this user {user_id}"},status=200)
        else:
            post = Post.objects.all()
        serializer= self.get_serializer(post,many=True)
        return Response({'data':serializer.data})
    
    def distroy(self,request,post_id=None):
        try:
           post =Post.objects.filter(id=post_id,user=request.user)
        except:
            return ValidationError("no rights to delete this post")
        if post.exists():
            post.delete()
            return Response({'post deleted'})
        else:
            return Response({'post not exist'})
    


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrCommentAuthor]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        if post_id:
            return Comment.objects.filter(post_id=post_id)
        return Comment.objects.all()
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')  
        print(f"Post ID from URL: {post_id}")  
        try:
            post = Post.objects.get(id=post_id) 
            print(f"Post found: {post}")  
        except Post.DoesNotExist:
            raise ValidationError("Post not found.")  

        serializer.save(post=post, user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def update(self, request, post_id, pk):
        try:
            comment = self.get_object()  
        except Comment.DoesNotExist:
            return Response({'detail': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is the owner of the comment
        if comment.user != request.user:
            return Response({'detail': 'You do not have permission to update this comment.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(comment, data=request.data, partial=True)  # Use partial=True if you want to allow partial updates
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("Post not found.")

       
        if Like.objects.filter(post=post, user=request.user).exists():
            raise ValidationError("You have already liked this post.")

      
        Like.objects.create(post=post, user=request.user)

        likes_count = Like.objects.filter(post=post).count()
       
        return Response({"message": f"Post liked successfully. Likes = {likes_count}"}, status=201)
    
    def delete(self,request,post_id):
        try:
            post=Post.objects.get(id=post_id)   
        except:
            raise NotFound("post not found")
        if Like.objects.filter(post=post).exists():
            Like.objects.filter(post=post).delete() 
            likes_count = Like.objects.filter(post=post).count
           
            return Response({"message": "Post unliked",
                             "post" : post_id }, status=201)
        
        else:
            return Response({'message':'Not any like found on this post'},status=201)
        
    def get(self,request,post_id):
        try:
            post=Post.objects.get(id=post_id)
        except:
            Response({"message" :"Post not found"},status=404)
        
        Like.objects.filter(post=post).count()
        return Response({
                 'Post' : post_id,
                'Likes' : Like.objects.filter(post=post).count()
                
            })
        
       
        
            
      


    

    