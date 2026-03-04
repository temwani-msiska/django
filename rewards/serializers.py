from rest_framework import serializers

from rewards.models import ActivityLog, Badge, EarnedBadge


class BadgeSerializer(serializers.ModelSerializer):
    earned = serializers.SerializerMethodField()

    class Meta:
        model = Badge
        fields = ('id', 'name', 'description', 'emoji', 'rarity', 'category', 'earned')

    def get_earned(self, obj):
        child = self.context.get('child')
        if not child:
            return False
        return EarnedBadge.objects.filter(child=child, badge=obj).exists()


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'
