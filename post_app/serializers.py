from .models import Post,Comment,Like
from rest_framework import serializers
from rest_framework import request

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title','content','image','id','user')
        read_only_fields = ['user']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user  # Set the user
        return super().create(validated_data)
    
    def update(self, instance, validate_data):
        instance.title = validate_data.get('title',instance.title)
        instance.content = validate_data.get('content',instance.content)
        instance.image = validate_data.get('image',instance.image)
        instance.save()
        return instance
    

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content','post']
        read_only_fields = ['post']
    
   
        
class LikeSerializer(serializers.ModelSerializer):
    model = Like
    fields = ['created_at'] 
    
    



    