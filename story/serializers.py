from rest_framework import serializers

from story.models import Scene, SceneProgress, StoryArc


class SceneSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Scene
        fields = (
            'id',
            'order',
            'title',
            'background_key',
            'characters_on_screen',
            'bubbles',
            'motions',
            'music_key',
            'sfx_keys',
            'next_action',
            'action_payload',
            'completed',
        )

    def get_completed(self, obj):
        child = self.context.get('child')
        if not child:
            return False
        return SceneProgress.objects.filter(child=child, scene=obj).exists()


class StoryArcListSerializer(serializers.ModelSerializer):
    scene_count = serializers.IntegerField(source='scenes.count', read_only=True)
    completed_count = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = StoryArc
        fields = ('id', 'title', 'description', 'arc_type', 'order', 'scene_count', 'completed_count', 'is_completed')

    def get_completed_count(self, obj):
        child = self.context.get('child')
        if not child:
            return 0
        return SceneProgress.objects.filter(child=child, scene__arc=obj).count()

    def get_is_completed(self, obj):
        child = self.context.get('child')
        if not child:
            return False
        total = obj.scenes.count()
        if total == 0:
            return False
        viewed = SceneProgress.objects.filter(child=child, scene__arc=obj).count()
        return viewed >= total


class StoryArcDetailSerializer(serializers.ModelSerializer):
    scenes = SceneSerializer(many=True, read_only=True)
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = StoryArc
        fields = ('id', 'title', 'description', 'arc_type', 'order', 'scenes', 'is_completed')

    def get_is_completed(self, obj):
        child = self.context.get('child')
        if not child:
            return False
        total = obj.scenes.count()
        if total == 0:
            return False
        viewed = SceneProgress.objects.filter(child=child, scene__arc=obj).count()
        return viewed >= total


class StoryArcRefSerializer(serializers.ModelSerializer):
    """Lightweight reference serializer for embedding in mission responses."""

    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = StoryArc
        fields = ('id', 'title', 'arc_type', 'is_completed')

    def get_is_completed(self, obj):
        child = self.context.get('child')
        if not child:
            return False
        total = obj.scenes.count()
        if total == 0:
            return False
        viewed = SceneProgress.objects.filter(child=child, scene__arc=obj).count()
        return viewed >= total
