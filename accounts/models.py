import uuid

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import AbstractUser
from django.db import models


class ParentUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)
    confirmation_token = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    confirmation_token_created_at = models.DateTimeField(null=True, blank=True)
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='accounts_parentuser_set',
        related_query_name='accounts_parentuser',
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='accounts_parentuser_set',
        related_query_name='accounts_parentuser',
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']


class ChildProfile(models.Model):
    AVATAR_CHOICES = [
        ('byte', 'Byte'),
        ('pixel', 'Pixel'),
        ('nova', 'Nova'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='children')
    nickname = models.CharField(max_length=30)
    pin = models.CharField(max_length=128)
    avatar_character = models.CharField(max_length=10, choices=AVATAR_CHOICES)
    avatar_url = models.URLField(blank=True)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    screen_time_limit_minutes = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    current_rank = models.ForeignKey(
        'rewards.Rank', null=True, blank=True, on_delete=models.SET_NULL, related_name='children'
    )

    class Meta:
        unique_together = ('parent', 'nickname')


class ChildPreferences(models.Model):
    child = models.OneToOneField(ChildProfile, on_delete=models.CASCADE, related_name='preferences')
    sound_enabled = models.BooleanField(default=True)
    music_enabled = models.BooleanField(default=True)
    high_contrast = models.BooleanField(default=False)
    public_profile = models.BooleanField(default=True)
    chat_locked = models.BooleanField(default=True)
