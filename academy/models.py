from django.db import models


class LearningTrack(models.Model):
    id = models.SlugField(primary_key=True)
    title = models.CharField(max_length=50)
    description = models.TextField()
    icon = models.CharField(max_length=10)
    color = models.CharField(max_length=7)
    order = models.IntegerField(default=0)


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
