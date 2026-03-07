from rest_framework import serializers

from characters.serializers import CharacterSerializer
from missions.models import (
    BossBattle, BossBattlePhase, BossBattleProgress,
    Mission, MissionProgress, MissionReward, MissionStep, StepProgress,
)
from story.models import SceneProgress
from story.serializers import StoryArcRefSerializer


class MissionStepSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = MissionStep
        fields = ('id', 'num', 'step_type', 'title', 'description', 'hint', 'content', 'validation_type', 'validation_value', 'status')

    def get_status(self, obj):
        mission_progress = self.context.get('mission_progress')
        if not mission_progress:
            return 'locked'
        step_progress = StepProgress.objects.filter(mission_progress=mission_progress, step=obj).first()
        return step_progress.status if step_progress else 'locked'


class MissionRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionReward
        fields = ('type', 'label', 'value', 'badge')


class BossBattlePhaseSerializer(serializers.ModelSerializer):
    leader_character_detail = CharacterSerializer(source='leader_character', read_only=True)

    class Meta:
        model = BossBattlePhase
        fields = ['id', 'phase_number', 'leader_character', 'leader_character_detail',
                  'title', 'description', 'challenge_type', 'content',
                  'intro_dialogue', 'success_dialogue', 'health_bar_label']


class BossBattleSerializer(serializers.ModelSerializer):
    phases = BossBattlePhaseSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()
    intro_arc = StoryArcRefSerializer(read_only=True)
    victory_arc = StoryArcRefSerializer(read_only=True)

    class Meta:
        model = BossBattle
        fields = ['id', 'title', 'description', 'total_phases', 'phases',
                  'intro_arc', 'victory_arc', 'defeat_dialogue', 'xp_bonus', 'progress']

    def get_progress(self, obj):
        child = self.context.get('child')
        if not child:
            return None
        progress = BossBattleProgress.objects.filter(child=child, boss_battle=obj).first()
        if not progress:
            return {'current_phase': 0, 'status': 'not_started', 'attempts': 0}
        return {
            'current_phase': progress.current_phase,
            'status': progress.status,
            'attempts': progress.attempts,
        }


class MissionSerializer(serializers.ModelSerializer):
    character_slug = serializers.SlugRelatedField(source='character', slug_field='slug', read_only=True)
    status = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    steps = MissionStepSerializer(many=True, read_only=True)
    rewards = MissionRewardSerializer(many=True, read_only=True)
    intro_arc = StoryArcRefSerializer(read_only=True)
    outro_arc = StoryArcRefSerializer(read_only=True)
    requires_arc = StoryArcRefSerializer(read_only=True)
    boss_battle = BossBattleSerializer(read_only=True)

    class Meta:
        model = Mission
        fields = (
            'id',
            'num',
            'title',
            'description',
            'long_description',
            'character_slug',
            'difficulty',
            'xp',
            'coins',
            'skills',
            'mentor_tip',
            'why_learn_this',
            'estimated_minutes',
            'starter_code',
            'language',
            'unlock_after',
            'is_active',
            'status',
            'progress',
            'steps',
            'rewards',
            'intro_arc',
            'outro_arc',
            'requires_arc',
            'boss_battle',
        )

    def _is_arc_completed(self, arc, child):
        if not arc or not child:
            return True
        total = arc.scenes.count()
        if total == 0:
            return True
        viewed = SceneProgress.objects.filter(child=child, scene__arc=arc).count()
        return viewed >= total

    def get_status(self, obj):
        child = self.context.get('child')
        if not child:
            return 'locked'
        progress = MissionProgress.objects.filter(child=child, mission=obj).first()
        if progress:
            return progress.status
        # Check mission prerequisite
        if obj.unlock_after is not None:
            prereq = MissionProgress.objects.filter(child=child, mission=obj.unlock_after, status='completed').exists()
            if not prereq:
                return 'locked'
        # Check story arc prerequisite
        if obj.requires_arc and not self._is_arc_completed(obj.requires_arc, child):
            return 'locked'
        return 'available'

    def get_progress(self, obj):
        child = self.context.get('child')
        if not child:
            return 0
        progress = MissionProgress.objects.filter(child=child, mission=obj).first()
        return progress.progress if progress else 0
