from rest_framework import serializers

from academy.models import LearningTrack, Lesson, LessonProgress


class LessonSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = '__all__'

    def get_completed(self, obj):
        child = self.context.get('child')
        if not child:
            return False
        return LessonProgress.objects.filter(child=child, lesson=obj, completed=True).exists()


class LearningTrackSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = LearningTrack
        fields = '__all__'
