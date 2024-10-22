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
           paginator = CustomPagination(request, post, page_size=5)
       
        paginated_data = paginator.paginated_data

        serializer= self.get_serializer(paginated_data,many=True)
        return paginator.get_paginated_response({'data':serializer.data})
    
    def destroy(self,request,post_id=None):
        post =Post.objects.get_object_or_404(id=post_id,user=request.user)
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
        post = Post.objects.get_object_or_404(id=post_id) 
        serializer.save(post=post, user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def update(self, request, post_id, pk):
        comment = get_object_or_404(Comment, id=pk, post_id=post_id)
        if comment.user != request.user:
            return Response({'detail': 'You do not have permission to update'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(comment, data=request.data, partial=True)  # Use partial=True if you want to allow partial updates
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class LikeView(APIView):
    permission_classes = [IsAuthenticated]
    

    def post(self, request, post_id):
        post = Post.objects.get_object_or_404(id=post_id)
        if Like.objects.filter(post=post, user=request.user).exists():
            raise ValidationError("You have already liked this post.")

      
        Like.objects.create(post=post, user=request.user)

        likes_count = Like.objects.filter(post=post).count()
       
        return Response({"message": f"Post liked successfully. Likes = {likes_count}"}, status=201)
    
    def delete(self,request,post_id):
    
        post=Post.objects.get_object_or_404(id=post_id)   
        
        if Like.objects.filter(post=post).exists():
            Like.objects.filter(post=post).delete() 
            likes_count = Like.objects.filter(post=post).count
           
            return Response({"message": "Post unliked",
                             "post" : post_id }, status=201)
        
        else:
            return Response({'message':'Not any like found on this post'},status=201)
        
    def get(self,request,post_id):
        post=Post.objects.get_object_or_404(id=post_id)
        Like.objects.filter(post=post).count()
        return Response({
                 'Post' : post_id,
                'Likes' : Like.objects.filter(post=post).count()
                
            })
        
       
        
            
      


    

    