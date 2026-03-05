from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import get_child_from_request
from core.utils import complete_mission, is_arc_completed
from missions.models import Mission, MissionProgress
from missions.serializers import MissionSerializer


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
