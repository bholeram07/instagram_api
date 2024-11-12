from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Post

@shared_task
def permanently_delete_posts():
    cutoff_date = timezone.now() - timedelta(days=15)
    posts_to_delete = Post.objects.filter(is_deleted=True, deleted_at__lte=cutoff_date)
    posts_to_delete.delete()


@shared_task
def delete_soft_deleted_comments():
    cutoff_date = timezone.now() - timedelta(days=15)
    comments_to_delete = Comment.objects.filter(is_deleted=True, deleted_at__lte=cutoff_date)
    comments_to_delete.delete()
    