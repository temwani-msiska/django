from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import get_child_from_request
from story.models import Scene, SceneProgress, StoryArc
from story.serializers import StoryArcDetailSerializer, StoryArcListSerializer


class StoryArcListView(generics.ListAPIView):
    serializer_class = StoryArcListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StoryArc.objects.filter(is_active=True)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['child'] = get_child_from_request(self.request)
        return context


class StoryArcDetailView(generics.RetrieveAPIView):
    queryset = StoryArc.objects.filter(is_active=True)
    serializer_class = StoryArcDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['child'] = get_child_from_request(self.request)
        return context


class SceneCompleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        child = get_child_from_request(request)
        if not child:
            return Response(
                {'detail': 'Child profile required.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            scene = Scene.objects.select_related('arc').get(id=id)
        except Scene.DoesNotExist:
            return Response(
                {'detail': 'Scene not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        SceneProgress.objects.get_or_create(child=child, scene=scene)

        # Check if the whole arc is now completed
        arc = scene.arc
        total = arc.scenes.count()
        viewed = SceneProgress.objects.filter(child=child, scene__arc=arc).count()
        arc_completed = viewed >= total

        return Response({
            'sceneId': str(scene.id),
            'arcId': arc.id,
            'arcCompleted': arc_completed,
            'scenesViewed': viewed,
            'scenesTotal': total,
        })
