import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("이메일", unique=True)
    name = models.CharField("이름", max_length=50)
    is_active = models.BooleanField("활성화", default=False)
    is_staff = models.BooleanField("스태프", default=False)
    date_joined = models.DateTimeField("가입일", default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return f"[User #{self.id:04d}] {self.email} ({self.name})"


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(
        "user.User",
        verbose_name="사용자",
        on_delete=models.CASCADE,
        related_name="email_verification",
    )
    token = models.UUIDField("토큰", default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField("생성일", auto_now_add=True)
    expires_at = models.DateTimeField("만료일")

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"[EmailVerificationToken] {self.user.email}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        "user.User",
        verbose_name="사용자",
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token = models.UUIDField("토큰", default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField("생성일", auto_now_add=True)
    expires_at = models.DateTimeField("만료일")
    is_used = models.BooleanField("사용 여부", default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"[PasswordResetToken] {self.user.email}"
