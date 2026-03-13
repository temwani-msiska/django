import uuid

from django.db import models


class LearningTrack(models.Model):
    id = models.SlugField(primary_key=True)
    title = models.CharField(max_length=50)
    description = models.TextField()
    icon = models.CharField(max_length=10)
    color = models.CharField(max_length=7)
    order = models.IntegerField(default=0)
    character = models.ForeignKey(
        'characters.Character',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tracks',
        help_text='The SHERO character who teaches this track',
    )


class Lesson(models.Model):
    id = models.SlugField(primary_key=True)
    track = models.ForeignKey(LearningTrack, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.CharField(max_length=20)
    order = models.IntegerField(default=0)
    unlock_after = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)


class LessonProgress(models.Model):
    child = models.ForeignKey('accounts.ChildProfile', on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('child', 'lesson')


class LessonStep(models.Model):
    STEP_TYPE_CHOICES = [
        ('explanation', 'Explanation'),
        ('example', 'Example'),
        ('guided_coding', 'Guided Coding'),
        ('multiple_choice', 'Multiple Choice'),
        ('fill_in', 'Fill In'),
        ('debugging', 'Debugging'),
        ('checkpoint', 'Checkpoint Question'),
        ('mini_challenge', 'Mini Challenge'),
        ('reflection', 'Reflection'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='steps')
    number = models.PositiveIntegerField()
    step_type = models.CharField(max_length=30, choices=STEP_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    content = models.JSONField(default=dict)
    hint = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['number']
        unique_together = ('lesson', 'number')


class LessonStepProgress(models.Model):
    STATUS_CHOICES = [
        ('locked', 'Locked'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey('accounts.ChildProfile', on_delete=models.CASCADE, related_name='lesson_step_progress')
    step = models.ForeignKey(LessonStep, on_delete=models.CASCADE, related_name='progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='locked')
    submitted_answer = models.JSONField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('child', 'step')
