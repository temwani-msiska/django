from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import get_child_from_request
from core.utils import complete_mission, is_arc_completed
from missions.models import (
    BossBattle, BossBattlePhase, BossBattleProgress,
    Mission, MissionProgress, MissionStep, StepProgress,
)
from missions.serializers import BossBattleSerializer, MissionSerializer
from playground.validators import validate_step_answer


class MissionListView(generics.ListAPIView):
    serializer_class = MissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Mission.objects.filter(is_active=True).order_by('num')
        character = self.request.query_params.get('character')
        if character:
            queryset = queryset.filter(character__slug=character)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['child'] = get_child_from_request(self.request)
        return context


class MissionDetailView(generics.RetrieveAPIView):
    queryset = Mission.objects.filter(is_active=True)
    serializer_class = MissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        child = get_child_from_request(self.request)
        context['child'] = child
        if child:
            context['mission_progress'] = MissionProgress.objects.filter(child=child, mission=self.get_object()).first()
        return context


class MissionStartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        child = get_child_from_request(request)
        mission = Mission.objects.get(id=id)

        # Enforce story arc prerequisite
        if mission.requires_arc and not is_arc_completed(child, mission.requires_arc):
            return Response(
                {'detail': f'You must complete the story "{mission.requires_arc.title}" first.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        progress, _ = MissionProgress.objects.get_or_create(child=child, mission=mission, defaults={'status': 'in_progress', 'started_at': timezone.now()})
        if progress.status == 'available':
            progress.status = 'in_progress'
            progress.started_at = timezone.now()
            progress.save()
        return Response({'status': progress.status, 'progress': progress.progress})


class MissionSaveCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, id):
        child = get_child_from_request(request)
        progress = MissionProgress.objects.get(child=child, mission_id=id)
        progress.current_code = request.data.get('code', '')
        progress.save(update_fields=['current_code'])
        return Response({'currentCode': progress.current_code})


class MissionCompleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        child = get_child_from_request(request)
        mission = Mission.objects.get(id=id)

        # Enforce story arc prerequisite
        if mission.requires_arc and not is_arc_completed(child, mission.requires_arc):
            return Response(
                {'detail': f'You must complete the story "{mission.requires_arc.title}" first.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        complete_mission(child, mission)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MissionStepSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id, step_number):
        child = get_child_from_request(request)
        mission = get_object_or_404(Mission, id=id)
        step = get_object_or_404(MissionStep, mission=mission, num=step_number)

        answer = request.data.get('answer', {})

        # Use new content-based validation if content is populated, else fall back
        if step.content:
            result = validate_step_answer(step.step_type, step.content, answer)
        else:
            result = {'passed': True, 'feedback': 'Step completed!'}

        mission_completed = False
        if result['passed']:
            # Get or create mission progress
            mission_progress, _ = MissionProgress.objects.get_or_create(
                child=child, mission=mission,
                defaults={'status': 'in_progress', 'started_at': timezone.now()}
            )

            # Mark step completed
            step_progress, _ = StepProgress.objects.get_or_create(
                mission_progress=mission_progress, step=step,
                defaults={'status': 'locked'}
            )
            step_progress.status = 'completed'
            step_progress.completed_at = timezone.now()
            step_progress.save()

            # Unlock next step
            next_step = MissionStep.objects.filter(
                mission=mission, num=step.num + 1
            ).first()
            if next_step:
                StepProgress.objects.get_or_create(
                    mission_progress=mission_progress, step=next_step,
                    defaults={'status': 'active'}
                )

            # Update progress percentage
            total_steps = mission.steps.count()
            completed_steps = StepProgress.objects.filter(
                mission_progress=mission_progress, status='completed'
            ).count()
            mission_progress.progress = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
            mission_progress.save(update_fields=['progress'])

            # If all steps complete, trigger mission completion
            if completed_steps >= total_steps:
                complete_mission(child, mission)
                mission_completed = True

        return Response({
            'passed': result['passed'],
            'feedback': result['feedback'],
            'step_completed': result['passed'],
            'mission_completed': mission_completed,
        })


class BossBattleStartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        child = get_child_from_request(request)
        mission = get_object_or_404(Mission, id=id)

        try:
            boss_battle = mission.boss_battle
        except BossBattle.DoesNotExist:
            return Response(
                {'detail': 'This mission does not have a boss battle.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        progress, created = BossBattleProgress.objects.get_or_create(
            child=child, boss_battle=boss_battle,
            defaults={'current_phase': 1, 'status': 'in_progress', 'attempts': 1}
        )
        if not created:
            # Reset for a new attempt
            progress.current_phase = 1
            progress.status = 'in_progress'
            progress.attempts += 1
            progress.completed_at = None
            progress.save()

        serializer = BossBattleSerializer(boss_battle, context={'child': child, 'request': request})
        return Response(serializer.data)


class BossBattlePhaseSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id, phase_number):
        child = get_child_from_request(request)
        mission = get_object_or_404(Mission, id=id)

        try:
            boss_battle = mission.boss_battle
        except BossBattle.DoesNotExist:
            return Response(
                {'detail': 'This mission does not have a boss battle.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        phase = get_object_or_404(BossBattlePhase, boss_battle=boss_battle, phase_number=phase_number)
        progress = get_object_or_404(BossBattleProgress, child=child, boss_battle=boss_battle)

        answer = request.data.get('answer', {})
        result = validate_step_answer(phase.challenge_type, phase.content, answer)

        if not result['passed']:
            return Response({
                'passed': False,
                'feedback': result['feedback'],
                'defeat_dialogue': boss_battle.defeat_dialogue,
                'current_phase': progress.current_phase,
            })

        # Phase passed
        boss_completed = False
        response_data = {
            'passed': True,
            'feedback': result['feedback'],
            'success_dialogue': phase.success_dialogue,
        }

        if phase_number >= boss_battle.total_phases:
            # Final phase - boss defeated
            progress.status = 'completed'
            progress.completed_at = timezone.now()
            progress.save()

            # Award bonus XP
            child.xp += boss_battle.xp_bonus
            child.save(update_fields=['xp'])

            # Ensure mission progress exists and complete mission
            MissionProgress.objects.get_or_create(
                child=child, mission=mission,
                defaults={'status': 'in_progress', 'started_at': timezone.now()}
            )
            complete_mission(child, mission)
            boss_completed = True

            response_data['boss_completed'] = True
            response_data['xp_bonus'] = boss_battle.xp_bonus
            if boss_battle.victory_arc:
                response_data['victory_arc_id'] = boss_battle.victory_arc_id
        else:
            # Advance to next phase
            progress.current_phase = phase_number + 1
            progress.save()
            response_data['boss_completed'] = False
            response_data['next_phase'] = phase_number + 1

        return Response(response_data)
