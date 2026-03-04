import uuid

from django.db import models


class Badge(models.Model):
    id = models.SlugField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    emoji = models.CharField(max_length=10)
    rarity = models.CharField(max_length=20)
    category = models.CharField(max_length=30)


class EarnedBadge(models.Model):
    child = models.ForeignKey('accounts.ChildProfile', on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('child', 'badge')


class ActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey('accounts.ChildProfile', on_delete=models.CASCADE, related_name='activity_logs')
    type = models.CharField(max_length=30)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    xp_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
