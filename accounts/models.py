from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=225, blank=True)
    last_name = models.CharField(max_length=225, blank=True)
    
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField()
    
    failed_login_attempts = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True)
    locked_at = models.DateTimeField(blank=True)

    USERNAME_FIELD = 'email'
    objects = UserManager()
