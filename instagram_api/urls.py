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

from post_app.views import PostViewSet,CommentViewSet,LikeView
router = DefaultRouter()
router.register('posts', PostViewSet) 
router.register('comments', CommentViewSet)  
router.register(r'posts/(?P<post_id>\d+)/comments', CommentViewSet, basename='comments')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('',include(router.urls)),
    path('posts/<int:post_id>/comments/',CommentViewSet.as_view({'post': 'create','get':'list'}), name='comment-create'),
    path('posts/<int:user_id>/user',PostViewSet.as_view({'get': 'list'}), name="get-user-post"),
    # path('post/<int:post_id>/comments/',CommentViewSet.as_view({'get': 'list'}),name = "get-comment"),
    path('posts/<int:pk>/',PostViewSet.as_view({'delete':'destroy'})),
    path('posts/<int:post_id>/comments/<int:pk>/', CommentViewSet.as_view({'put' : 'update','get': 'retrieve', 'delete': 'destroy'}), name='comment-detail-delete'),
    path('posts/like/<int:post_id>/',LikeView.as_view()),
    path('posts/like/<int:post_id>/',LikeView.as_view()),
    path('posts/like/<int:post_id>/',LikeView.as_view())
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)