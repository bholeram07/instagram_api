from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True, null=True)
    other_social = models.CharField(max_length=30, blank=True, null=True)
    links = models.CharField(max_length=30, blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile/", null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_private = models.BooleanField(default=False, help_text="True if the account is private, False if public")
    is_staff = models.BooleanField(default=False)

    


    last_password_change = models.DateTimeField(null=True, blank=True)
    username_change_count = models.PositiveIntegerField(default=0)
    last_username_change = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        db_table = "user"

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_user = User.objects.get(pk=self.pk)
                if old_user.password != self.password:
                    self.last_password_change = timezone.now()
            except User.DoesNotExist:
                    pass
        super().save(*args, **kwargs)
    def __str__(self):
        return self.username


class OtpVerification(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE,to_field='id', db_column='user_id')
    otp = models.CharField(max_length=6)

    def is_expired(self):
        expiration_time = self.created_at + timedelta(minutes=5)
        return timezone.now() > expiration_time
    class Meta:
        db_table = 'user_otp'


class Follow(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]
    # The user who is following someone
    follower = models.ForeignKey(
        User, related_name='follower', on_delete=models.CASCADE
    )
    # The user being followed
    following = models.ForeignKey(
        User, related_name='following', on_delete=models.CASCADE,null =True
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='accepted'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        db_table = "follow"

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username} ({self.status})"
