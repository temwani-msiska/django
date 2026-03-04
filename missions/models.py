import uuid

from django.db import models


class Mission(models.Model):
    id = models.SlugField(primary_key=True)
    num = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    long_description = models.TextField()
    character = models.ForeignKey('characters.Character', on_delete=models.CASCADE, related_name='missions')
    difficulty = models.CharField(max_length=20)
    xp = models.IntegerField()
    coins = models.IntegerField(default=0)
    skills = models.JSONField(default=list)
    mentor_tip = models.TextField()
    why_learn_this = models.TextField()
    estimated_minutes = models.IntegerField()
    starter_code = models.TextField()
    language = models.CharField(max_length=20)
    unlock_after = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)


class MissionStep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='steps')
    num = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    hint = models.TextField(blank=True)
    validation_type = models.CharField(max_length=30)
    validation_value = models.TextField()


class MissionReward(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='rewards')
    type = models.CharField(max_length=20)
    label = models.CharField(max_length=50)
    value = models.IntegerField()
    badge = models.ForeignKey('rewards.Badge', null=True, blank=True, on_delete=models.SET_NULL)


class MissionProgress(models.Model):
    STATUS_CHOICES = [
        ('locked', 'locked'),
        ('available', 'available'),
        ('in_progress', 'in_progress'),
        ('completed', 'completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey('accounts.ChildProfile', on_delete=models.CASCADE, related_name='mission_progress')
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='locked')
    progress = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    current_code = models.TextField(blank=True)

    class Meta:
        unique_together = ('child', 'mission')


class StepProgress(models.Model):
    mission_progress = models.ForeignKey(MissionProgress, on_delete=models.CASCADE, related_name='step_progress')
    step = models.ForeignKey(MissionStep, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    completed_at = models.DateTimeField(null=True, blank=True)
