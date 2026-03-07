import uuid

from django.core.exceptions import ValidationError
from django.db import models


class StoryArc(models.Model):
    """A collection of scenes forming a narrative sequence (e.g. prologue, mission intro)."""

    id = models.SlugField(primary_key=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    arc_type = models.CharField(
        max_length=20,
        choices=[
            ('prologue', 'Prologue'),
            ('mission_intro', 'Mission Intro'),
            ('mission_outro', 'Mission Outro'),
            ('interlude', 'Interlude'),
        ],
    )
    order = models.IntegerField(default=0, help_text='Global display order for arc lists')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Scene(models.Model):
    """A single scene within a story arc — background, characters, dialogue, audio cues."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    arc = models.ForeignKey(StoryArc, on_delete=models.CASCADE, related_name='scenes')
    order = models.IntegerField()
    title = models.CharField(max_length=120, blank=True)

    # Visual
    background_key = models.CharField(max_length=80, help_text='Asset key for background image')
    characters_on_screen = models.JSONField(
        default=list,
        help_text='[{"assetKey": "byte-idle", "position": "center", "motion": "slide-in-left"}]',
    )

    # Dialogue / bubbles
    bubbles = models.JSONField(
        default=list,
        help_text='[{"speaker": "byte", "text": "Hello!", "type": "speech"}]',
    )

    # Motion / animation cues
    motions = models.JSONField(
        default=list,
        help_text='[{"target": "screen", "effect": "shake", "duration": 500}]',
    )

    # Audio
    music_key = models.CharField(max_length=80, blank=True, help_text='Background music asset key')
    sfx_keys = models.JSONField(default=list, help_text='["typing", "whoosh"]')

    # Progression
    next_action = models.CharField(
        max_length=20,
        default='next',
        choices=[
            ('next', 'Next Scene'),
            ('choice', 'Player Choice'),
            ('run_code', 'Run Code Challenge'),
            ('challenge', 'Inline Challenge'),
            ('end', 'End Arc'),
        ],
    )
    action_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text='Extra data for next_action, e.g. {"starterCode": "print()", "language": "python"}',
    )

    class Meta:
        ordering = ['arc', 'order']
        unique_together = ('arc', 'order')

    def clean(self):
        from story.schemas import validate_scene_data
        errors = validate_scene_data(self)
        if errors:
            raise ValidationError({'scene_data': errors})

    def __str__(self):
        return f'{self.arc_id} / Scene {self.order}'


class SceneProgress(models.Model):
    """Tracks that a child has viewed/completed a specific scene."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        'accounts.ChildProfile', on_delete=models.CASCADE, related_name='scene_progress'
    )
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, related_name='progress')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('child', 'scene')

    def __str__(self):
        return f'{self.child} viewed {self.scene}'
