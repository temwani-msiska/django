from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import ChildPreferences, ChildProfile, ParentUser
from core.utils import xp_for_level
from rewards.models import ActivityLog, EarnedBadge
from rewards.serializers import ActivityLogSerializer, BadgeSerializer


class ParentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentUser
        fields = ('id', 'email', 'name')


class ParentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = ParentUser
        fields = ('id', 'email', 'name', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = ParentUser(**validated_data)
        user.set_password(password)
        user.username = user.email
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
    badges = serializers.SerializerMethodField()
    activity = serializers.SerializerMethodField()

    def get_xp_to_next_level(self, obj):
        return max(xp_for_level(obj.level) - obj.xp, 0)

    def get_badges(self, obj):
        from rewards.models import Badge

        return BadgeSerializer(Badge.objects.all(), many=True, context={'child': obj}).data

    def get_activity(self, obj):
        logs = ActivityLog.objects.filter(child=obj).order_by('-created_at')[:10]
        return ActivityLogSerializer(logs, many=True).data


def tokens_for_user(user, child_id=None):
    refresh = RefreshToken.for_user(user)
    if child_id:
        refresh['child_id'] = str(child_id)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}
