
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

class BlacklistedToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True , null= True)
    other_social = models.CharField(max_length=30, blank=True,null =True)
    links = models.CharField(max_length=30,blank= True,null =True)
    profile_image = models.ImageField(upload_to= '\post',null =True) 
    # country_code = models.BigIntegerField(default=+91)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_password_change = models.DateTimeField(null= True,blank = True)
    username_change_count = models.PositiveIntegerField(default =0)
    last_username_change = models.DateTimeField(null = True ,blank = True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']
    
    class Meta:
        db_table = "User"
        
        
    def save(self,*args,**kwargs):
        if self.pk is not None:
            old_user = User.objects.get(pk=self.pk)
            if old_user.password != self.password :
                last_password_change = timezone.now()
        super.save(*args,**kwargs)
        
        
    def __str__(self):
        return self.email



