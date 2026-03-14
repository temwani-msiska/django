from rest_framework import serializers

from academy.models import LearningTrack, Lesson, LessonProgress, LessonStep, LessonStepProgress


class LessonStepSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    submitted_answer = serializers.SerializerMethodField()

    class Meta:
        model = LessonStep
        fields = ['id', 'number', 'step_type', 'title', 'content', 'hint', 'is_required', 'status', 'submitted_answer']

    def get_status(self, obj):
        child = self.context.get('child')
        if not child:
            return 'locked'
        progress = LessonStepProgress.objects.filter(child=child, step=obj).first()
        return progress.status if progress else 'locked'

    def get_submitted_answer(self, obj):
        child = self.context.get('child')
        if not child:
            return None
        progress = LessonStepProgress.objects.filter(child=child, step=obj).first()
        return progress.submitted_answer if progress else None


class LessonSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    locked = serializers.SerializerMethodField()
    slug = serializers.CharField(source='id', read_only=True)
    steps = LessonStepSerializer(many=True, read_only=True)
    step_count = serializers.SerializerMethodField()
    completed_steps = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'slug', 'title', 'description', 'duration', 'order',
                  'completed', 'locked', 'steps', 'step_count', 'completed_steps']

    def get_completed(self, obj):
        child = self.context.get('child')
        if not child:
            return False
        return LessonProgress.objects.filter(child=child, lesson=obj, completed=True).exists()

    def get_locked(self, obj):
        child = self.context.get('child')
        if not child:
            return True
        # If no unlock_after, the lesson is always available
        if obj.unlock_after is None:
            return False
        # Check if the prerequisite lesson is completed
        return not LessonProgress.objects.filter(
            child=child, lesson=obj.unlock_after, completed=True
        ).exists()

    def get_step_count(self, obj):
        return obj.steps.filter(is_required=True).count()

    def get_completed_steps(self, obj):
        child = self.context.get('child')
        if not child:
            return 0
        return LessonStepProgress.objects.filter(
            child=child,
            step__lesson=obj,
            step__is_required=True,
            status='completed'
        ).count()


class LearningTrackSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    slug = serializers.CharField(source='id', read_only=True)
    characterSlug = serializers.CharField(source='character.slug', read_only=True, default=None)
    characterName = serializers.CharField(source='character.name', read_only=True, default=None)

    class Meta:
        model = LearningTrack
        fields = ['id', 'slug', 'title', 'description', 'icon', 'color',
                  'order', 'characterSlug', 'characterName', 'lessons']


class LessonStepSubmitSerializer(serializers.Serializer):
    answer = serializers.JSONField(required=True)
