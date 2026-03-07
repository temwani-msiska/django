from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import get_child_from_request
from story.models import Scene, SceneProgress, StoryArc
from story.serializers import SceneSerializer, StoryArcDetailSerializer, StoryArcListSerializer


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


class SceneChoiceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, scene_id):
        child = get_child_from_request(request)
        if not child:
            return Response(
                {'detail': 'Child profile required.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            scene = Scene.objects.select_related('arc').get(id=scene_id)
        except Scene.DoesNotExist:
            return Response(
                {'detail': 'Scene not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if scene.next_action != 'choice':
            return Response(
                {'detail': 'This scene does not have choices.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        choice_index = request.data.get('choice_index')
        if choice_index is None:
            return Response(
                {'detail': 'choice_index is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        choices = scene.action_payload.get('choices', [])
        if not isinstance(choice_index, int) or choice_index < 0 or choice_index >= len(choices):
            return Response(
                {'detail': 'Invalid choice_index.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark current scene as viewed
        SceneProgress.objects.get_or_create(child=child, scene=scene)

        # Get the target scene
        target_order = choices[choice_index].get('next_scene_order')
        try:
            next_scene = Scene.objects.get(arc=scene.arc, order=target_order)
        except Scene.DoesNotExist:
            return Response(
                {'detail': f'Target scene with order {target_order} not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SceneSerializer(next_scene, context={'child': child, 'request': request})
        return Response(serializer.data)
