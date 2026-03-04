from django.utils import timezone
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from academy.models import LearningTrack, Lesson, LessonProgress
from academy.serializers import LearningTrackSerializer
from core.authentication import get_child_from_request


class LearningTrackListView(ListAPIView):
    serializer_class = LearningTrackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LearningTrack.objects.all().order_by('order')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['child'] = get_child_from_request(self.request)
        return context


class CompleteLessonView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        child = get_child_from_request(request)
        lesson = Lesson.objects.get(id=id)
        progress, _ = LessonProgress.objects.get_or_create(child=child, lesson=lesson)
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        return Response({'completed': True})
