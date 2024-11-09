from .models import Post, Comment, Like
from rest_framework import serializers
from rest_framework import request
from user.serializers import SignupSerializer


class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ("title", "content", "image", "id", "user","likes_count","comments",'created_at')
        read_only_fields = ["user",'likes_count','comments','created_at']
        
    def get_likes_count(self,obj):
        return Like.objects.filter(post=obj).count()  
    
    def get_comments(self,obj):
        return Comment.objects.filter(post = obj).count()
    

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """Exclude `likes_count` in POST requests"""
        representation = super().to_representation(instance)
        request = self.context.get("request")
        if request and (request.method == "POST" or request.method == "PUT"):
            representation.pop("likes_count", None)
            representation.pop("comments",None)
       
           
        
        return representation

    def update(self, instance, validate_data):
        instance.title = validate_data.get("title", instance.title)
        instance.content = validate_data.get("content", instance.content)
        instance.image = validate_data.get("image", instance.image)
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    # user = SignupSerializer(read_only=True)
    # post = PostSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'post', 'replies', 'user']
        read_only_fields = ["user","post"]

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    user = SignupSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ["created_at", "user", "post"]
        read_only_fields = ["user","post"]

