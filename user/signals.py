from .models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

@receiver(post_save, sender=User)
def blacklist_tokens(sender, instance, **kwargs):
    # Blacklist all tokens for the user
    OutstandingToken.objects.filter(user=instance).delete()