from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import ChildPreferences, ChildProfile
from core.utils import STREAK_MILESTONES, get_current_rank, get_next_rank, xp_for_level
from rewards.models import ActivityLog
from rewards.serializers import ActivityLogSerializer, BadgeSerializer, RankSerializer

User = get_user_model()


def _name_for_user(user):
    return getattr(user, 'name', '') or getattr(user, 'first_name', '') or getattr(user, 'username', '')


class ParentUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'name')

    def get_name(self, obj):
        return _name_for_user(obj)


class ParentRegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'password')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value.lower()

    def create(self, validated_data):
        import uuid

        from django.utils import timezone

        name = validated_data.pop('name', '')
        password = validated_data.pop('password')
        user = User(**validated_data)
        if hasattr(user, 'name'):
            user.name = name
        else:
            user.first_name = name
        user.username = user.email
        user.set_password(password)
        user.confirmation_token = uuid.uuid4()
        user.confirmation_token_created_at = timezone.now()
        user.save()
        return user


class ChildPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildPreferences
        exclude = ('child',)


class ChildProfileSerializer(serializers.ModelSerializer):
    preferences = ChildPreferencesSerializer(read_only=True)

    class Meta:
        model = ChildProfile
        exclude = ('pin',)


class ChildCreateSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(write_only=True)

    class Meta:
        model = ChildProfile
        fields = ('id', 'nickname', 'pin', 'avatar_character')

    def create(self, validated_data):
        validated_data['pin'] = make_password(validated_data['pin'])
        child = ChildProfile.objects.create(parent=self.context['request'].user, **validated_data)
        ChildPreferences.objects.create(child=child)
        return child


class ChildLoginSerializer(serializers.Serializer):
    parent_email = serializers.EmailField()
    nickname = serializers.CharField()
    pin = serializers.CharField()

    def validate(self, attrs):
        try:
            child = ChildProfile.objects.get(parent__email=attrs['parent_email'], nickname=attrs['nickname'])
        except ChildProfile.DoesNotExist as exc:
            raise serializers.ValidationError('Invalid child credentials') from exc
        if not check_password(attrs['pin'], child.pin):
            raise serializers.ValidationError('Invalid child credentials')
        attrs['child'] = child
        return attrs


class PlayerProgressSerializer(serializers.Serializer):
    xp = serializers.IntegerField()
    level = serializers.IntegerField()
    streak = serializers.IntegerField()
    xp_to_next_level = serializers.SerializerMethodField()
    total_missions = serializers.SerializerMethodField()
    missions_completed = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    lessons_completed = serializers.SerializerMethodField()
    current_rank = serializers.SerializerMethodField()
    next_rank = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()
    recent_activity = serializers.SerializerMethodField()
    streak_milestone_next = serializers.SerializerMethodField()

    def get_xp_to_next_level(self, obj):
        return max(xp_for_level(obj.level) - obj.xp, 0)

    def get_badges(self, obj):
        from rewards.models import Badge

        return BadgeSerializer(Badge.objects.all(), many=True, context={'child': obj}).data

    def get_recent_activity(self, obj):
        logs = ActivityLog.objects.filter(child=obj).order_by('-created_at')[:10]
        return ActivityLogSerializer(logs, many=True).data

    def get_total_missions(self, obj):
        from missions.models import Mission

        return Mission.objects.filter(is_active=True).count()

    def get_missions_completed(self, obj):
        return obj.mission_progress.filter(status='completed').count()

    def get_total_lessons(self, obj):
        from academy.models import Lesson

        return Lesson.objects.count()

    def get_lessons_completed(self, obj):
        from academy.models import LessonProgress

        return LessonProgress.objects.filter(child=obj, completed=True).count()

    def get_current_rank(self, obj):
        rank = get_current_rank(obj)
        return RankSerializer(rank).data if rank else None

    def get_next_rank(self, obj):
        result = get_next_rank(obj)
        if result:
            return {
                'rank': RankSerializer(result['rank']).data,
                'missions_needed': result['missions_needed'],
            }
        return None

    def get_streak_milestone_next(self, obj):
        milestones = sorted(STREAK_MILESTONES.keys())
        for milestone in milestones:
            if obj.streak < milestone:
                return {'days_needed': milestone - obj.streak, 'milestone': milestone}
        return None


def tokens_for_user(user, child_id=None):
    refresh = RefreshToken.for_user(user)
    if child_id:
        refresh['child_id'] = str(child_id)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}
