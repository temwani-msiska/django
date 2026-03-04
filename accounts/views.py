from django.contrib.auth import authenticate
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import ChildProfile
from accounts.serializers import (
    ChildCreateSerializer,
    ChildLoginSerializer,
    ChildPreferencesSerializer,
    ChildProfileSerializer,
    ParentRegisterSerializer,
    ParentUserSerializer,
    PlayerProgressSerializer,
    tokens_for_user,
)
from core.authentication import get_child_from_request
from core.utils import get_rank
from rewards.models import ActivityLog, EarnedBadge


class ParentRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ParentRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({**ParentUserSerializer(user).data, 'tokens': tokens_for_user(user)}, status=status.HTTP_201_CREATED)


class ParentLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = authenticate(request, username=request.data.get('email'), password=request.data.get('password'))
        if not user:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'tokens': tokens_for_user(user), 'parent': ParentUserSerializer(user).data})


class ChildCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChildCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        child = serializer.save()
        return Response({'child': ChildProfileSerializer(child).data}, status=status.HTTP_201_CREATED)


class ChildLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ChildLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        child = serializer.validated_data['child']
        return Response({'tokens': tokens_for_user(child.parent, child_id=child.id), 'user': ChildProfileSerializer(child).data})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get('refresh')
    if refresh_token:
        token = RefreshToken(refresh_token)
        token.blacklist()
    return Response(status=status.HTTP_204_NO_CONTENT)


class ParentMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        children_data = []
        for child in request.user.children.all():
            missions_completed = child.mission_progress.filter(status='completed').count()
            children_data.append(
                {
                    **ChildProfileSerializer(child).data,
                    'hours_played': round(child.xp / 50, 1),
                    'badges_earned': EarnedBadge.objects.filter(child=child).count(),
                    'rank': get_rank(missions_completed),
                    'skill_mastery': min(100, child.level * 10),
                    'learning_path': child.avatar_character,
                }
            )
        return Response({'id': request.user.id, 'email': request.user.email, 'name': request.user.name, 'children': children_data})


class ChildMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        child = get_child_from_request(request)
        return Response(ChildProfileSerializer(child).data)

    def patch(self, request):
        child = get_child_from_request(request)
        serializer = ChildProfileSerializer(child, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChildProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        child = get_child_from_request(request)
        return Response(PlayerProgressSerializer(child).data)


class ChildPreferencesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        child = get_child_from_request(request)
        serializer = ChildPreferencesSerializer(child.preferences, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChildActivityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        child = ChildProfile.objects.get(id=id, parent=request.user)
        logs = ActivityLog.objects.filter(child=child).order_by('-created_at')
        return Response([{'type': l.type, 'title': l.title, 'description': l.description, 'xpEarned': l.xp_earned, 'createdAt': l.created_at} for l in logs])


class ChildScreenTimeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, id):
        child = ChildProfile.objects.get(id=id, parent=request.user)
        child.screen_time_limit_minutes = request.data.get('screen_time_limit_minutes', child.screen_time_limit_minutes)
        child.save(update_fields=['screen_time_limit_minutes'])
        return Response({'screen_time_limit_minutes': child.screen_time_limit_minutes})
