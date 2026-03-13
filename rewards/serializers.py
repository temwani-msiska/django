from rest_framework import serializers

from rewards.models import ActivityLog, Badge, EarnedBadge, Rank


class BadgeSerializer(serializers.ModelSerializer):
    earned = serializers.SerializerMethodField()
    earned_at = serializers.SerializerMethodField()

    class Meta:
        model = Badge
        fields = ('id', 'name', 'description', 'emoji', 'rarity', 'category', 'earned', 'earned_at')

    def get_earned(self, obj):
        child = self.context.get('child')
        if not child:
            return False
        return EarnedBadge.objects.filter(child=child, badge=obj).exists()

    def get_earned_at(self, obj):
        child = self.context.get('child')
        if not child:
            return None
        earned = EarnedBadge.objects.filter(child=child, badge=obj).first()
        return earned.earned_at if earned else None


class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields = ('slug', 'name', 'title', 'emoji', 'min_missions', 'color', 'description', 'order')


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'
