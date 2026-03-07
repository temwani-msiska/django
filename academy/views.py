from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from academy.models import LearningTrack, Lesson, LessonProgress, LessonStep, LessonStepProgress
from academy.serializers import LearningTrackSerializer, LessonSerializer, LessonStepSubmitSerializer
from core.authentication import get_child_from_request
from core.utils import check_level_up
from playground.validators import validate_step_answer


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

    def post(self, request, slug):
        child = get_child_from_request(request)
        lesson = Lesson.objects.get(id=slug)
        progress, _ = LessonProgress.objects.get_or_create(child=child, lesson=lesson)
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        return Response({'completed': True})


class LessonDetailView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'slug'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['child'] = get_child_from_request(self.request)
        return context


class LessonStartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        child = get_child_from_request(request)
        lesson = get_object_or_404(Lesson, id=slug)
        first_step = lesson.steps.order_by('number').first()
        if first_step:
            LessonStepProgress.objects.get_or_create(
                child=child, step=first_step,
                defaults={'status': 'active'}
            )
        serializer = LessonSerializer(lesson, context={'child': child, 'request': request})
        return Response(serializer.data)


class LessonStepSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug, step_number):
        child = get_child_from_request(request)
        lesson = get_object_or_404(Lesson, id=slug)
        step = get_object_or_404(LessonStep, lesson=lesson, number=step_number)

        serializer = LessonStepSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer = serializer.validated_data['answer']

        result = validate_step_answer(step.step_type, step.content, answer)

        lesson_completed = False
        if result['passed']:
            progress, _ = LessonStepProgress.objects.get_or_create(
                child=child, step=step,
                defaults={'status': 'active'}
            )
            progress.status = 'completed'
            progress.submitted_answer = answer
            progress.completed_at = timezone.now()
            progress.save()

            # Unlock next step
            next_step = LessonStep.objects.filter(
                lesson=lesson, number=step.number + 1
            ).first()
            if next_step:
                LessonStepProgress.objects.get_or_create(
                    child=child, step=next_step,
                    defaults={'status': 'active'}
                )

            # Check if lesson is complete
            required_steps = lesson.steps.filter(is_required=True).count()
            completed_steps = LessonStepProgress.objects.filter(
                child=child,
                step__lesson=lesson,
                step__is_required=True,
                status='completed'
            ).count()

            if completed_steps >= required_steps:
                LessonProgress.objects.update_or_create(
                    child=child, lesson=lesson,
                    defaults={'completed': True, 'completed_at': timezone.now()}
                )
                child.xp += 50
                child.save(update_fields=['xp'])
                check_level_up(child)
                lesson_completed = True

        return Response({
            'passed': result['passed'],
            'feedback': result['feedback'],
            'step_completed': result['passed'],
            'lesson_completed': lesson_completed,
        })


class SaveLessonDraftView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, slug, step_number):
        child = get_child_from_request(request)
        lesson = get_object_or_404(Lesson, id=slug)
        step = get_object_or_404(LessonStep, lesson=lesson, number=step_number)

        progress, _ = LessonStepProgress.objects.get_or_create(
            child=child, step=step,
            defaults={'status': 'active'}
        )
        progress.submitted_answer = {'draft_code': request.data.get('code', '')}
        progress.save(update_fields=['submitted_answer'])

        return Response({'saved': True})

    def get(self, request, slug, step_number):
        child = get_child_from_request(request)
        lesson = get_object_or_404(Lesson, id=slug)
        step = get_object_or_404(LessonStep, lesson=lesson, number=step_number)

        progress = LessonStepProgress.objects.filter(child=child, step=step).first()
        draft = progress.submitted_answer if progress else None

        return Response({'draft': draft})
