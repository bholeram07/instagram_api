"""
URL configuration for practise project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from user import urls
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from post_app import views
from post_app.views import SavedPostView

from post_app.views import PostViewSet,CommentViewSet,LikeView
router = DefaultRouter()
router.register('posts', PostViewSet) 
router.register('comments', CommentViewSet)  
router.register(r'posts/(?P<post_id>\d+)/comments', CommentViewSet, basename='comments')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('',include(router.urls)),
    
    path('post/<str:post_id>/comment/',CommentViewSet.as_view({'post': 'create','get':'list'}), name='comment-create'),
    path('comment/<str:post_id>/reply/', CommentViewSet.as_view({'post': 'create'}), name='reply-comment'),
    path('posts/<str:user_id>/user',PostViewSet.as_view({'get':'list'}), name="get-user-post"),
    path('like/<str:post_id>/',LikeView.as_view()),
    path('save-post/<str:post_id>/', SavedPostView.as_view(), name='save-post'),
    
    path('saved-posts/', SavedPostView.as_view(), name='saved-posts-list')
   
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)