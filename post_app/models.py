from django.db import models
from user.models import User  


#Post Model

class Post(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length = 25)
    content = models.TextField()
    image = models.ImageField(upload_to = 'posts/', null= True, blank = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = "Post"


#comment Model
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self',null=True,blank=True, on_delete=models.CASCADE , related_name = 'replies')
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    
    def __str__(self):
        return f'{self.user} comment {self.post}'
    
    class Meta:
        db_table = "Comment"

#like Model
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    class Meta:
        unique_together = ('post', 'user') 
        db_table = 'Like'
        
    def __str__(self):    
        return f'{self.user} liked {self.post}'
    
   


