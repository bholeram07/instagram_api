
from django.urls import path,include
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('create/',PostView.as_view()),
    path('get/',PostView.as_view()),
    path('delete/<int:post_id>',PostView.as_view()),
    path('update/<int:post_id>',PostView.as_view()),
    path('create-comment/<int:post_id>',CommentView.as_view()),
    path('get-comment/<int:post_id>',CommentView.as_view()),
    path('delete-comment/<int:comment_id>',CommentView.as_view()),
    path('update-comment/<int:comment_id>',CommentView.as_view()),
    path('likes/create/<int:post_id>',LikeView.as_view(),name="Like-create")
]
