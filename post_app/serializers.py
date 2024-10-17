from .models import Post,Comment,Like
from rest_framework import serializers
from rest_framework import request

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title','content','image')
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user  # Set the user
        return super().create(validated_data)
    
    def update(self, instance, validate_data):
        instance.title = validate_data.get('title',instance.title)
        instance.content = validate_data.get('content',instance.content)
        instance.image = validate_data.get('image',instance.image)
        instance.save()
        return instance
    
class GetPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields = ('id', 'title', 'content', 'image','user') 

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content']
    def create(self, validated_data):
        post = self.context.get('post')
        user = self.context['request'].user 
        comment = Comment.objects.create(post=post, user=user, **validated_data)
        return comment
        
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('created_at',)
        
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user  
        return super().create(validated_data)

class GetLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Like
        fields = ('id','created_at','post') 

    