
from django.urls import path,include
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('create/',PostView.as_view(),name="create-post"),
    path('get/',PostView.as_view(),name = "get-post"),
    path('delete/<int:post_id>',PostView.as_view(), name="delete-post"),
    path('update/<int:post_id>',PostView.as_view(), name = "update-post"),
    path('post-comment/<int:post_id>',CommentView.as_view(),name="create-comment"),
    path('get-comment/<int:post_id>',CommentView.as_view(), name="get-comment"  ),
    path('delete-comment/<int:comment_id>',CommentView.as_view(), name="delete-comment"),
    path('update-comment/<int:comment_id>',CommentView.as_view(), name = "update-comment" ),
    path('likes/create/<int:post_id>',LikeView.as_view(),name="Like-create")
]
