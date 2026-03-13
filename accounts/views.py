from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
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
from core.permissions import IsParent, IsParentOfChild
from core.utils import get_current_rank, get_rank
from rewards.models import ActivityLog, Badge, EarnedBadge
from rewards.serializers import ActivityLogSerializer, RankSerializer

User = get_user_model()


class ParentRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ParentRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        from accounts.emails import send_verification_email
        send_verification_email(user)

        return Response(
            {
                **ParentUserSerializer(user).data,
                'tokens': tokens_for_user(user),
                'email_verification_required': True,
            },
            status=status.HTTP_201_CREATED,
        )


class ParentLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
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
        name = getattr(request.user, 'name', '') or getattr(request.user, 'first_name', '') or request.user.username
        return Response({'id': request.user.id, 'email': request.user.email, 'name': name, 'children': children_data})


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


class ConfirmEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        import uuid as uuid_mod
        from datetime import timedelta

        from django.utils import timezone

        token = request.query_params.get('token')
        if not token:
            return Response({'detail': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token_uuid = uuid_mod.UUID(str(token))
        except (ValueError, AttributeError):
            return Response({'detail': 'Invalid confirmation link.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(confirmation_token=token_uuid).first()
        if not user:
            return Response({'detail': 'Invalid confirmation link.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.email_verified:
            return Response({'detail': 'Email already verified.'})

        if user.confirmation_token_created_at and user.confirmation_token_created_at < timezone.now() - timedelta(hours=24):
            return Response(
                {'detail': 'This link has expired. Please request a new confirmation email.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.email_verified = True
        user.confirmation_token = None
        user.confirmation_token_created_at = None
        user.save(update_fields=['email_verified', 'confirmation_token', 'confirmation_token_created_at'])
        return Response({'detail': 'Email verified successfully.'})


class ResendConfirmationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        import uuid as uuid_mod
        from datetime import timedelta

        from django.core.cache import cache
        from django.utils import timezone

        email = (request.data.get('email') or '').lower().strip()
        safe_response = Response({'detail': 'If an account exists with this email, a new confirmation link has been sent.'})

        if not email:
            return safe_response

        # Rate limit: 1 per 60s per email
        cache_key = f'resend_confirm:{email}'
        if cache.get(cache_key):
            return safe_response

        user = User.objects.filter(email__iexact=email).first()
        if not user or user.email_verified:
            return safe_response

        user.confirmation_token = uuid_mod.uuid4()
        user.confirmation_token_created_at = timezone.now()
        user.save(update_fields=['confirmation_token', 'confirmation_token_created_at'])

        from accounts.emails import send_verification_email
        send_verification_email(user)

        cache.set(cache_key, True, 60)
        return safe_response


class XPBreakdownView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        child = get_child_from_request(request)

        mission_xp = ActivityLog.objects.filter(
            child=child, type='mission_completed'
        ).aggregate(total=Sum('xp_earned'))['total'] or 0

        lesson_xp = ActivityLog.objects.filter(
            child=child, type='lesson_completed'
        ).aggregate(total=Sum('xp_earned'))['total'] or 0

        streak_xp = ActivityLog.objects.filter(
            child=child, type='badge_earned',
            title__icontains='streak'
        ).aggregate(total=Sum('xp_earned'))['total'] or 0

        boss_xp = ActivityLog.objects.filter(
            child=child, type='boss_completed'
        ).aggregate(total=Sum('xp_earned'))['total'] or 0

        level_bonus_xp = ActivityLog.objects.filter(
            child=child, type='level_up'
        ).aggregate(total=Sum('xp_earned'))['total'] or 0

        return Response({
            'total_xp': child.xp,
            'breakdown': {
                'missions': mission_xp,
                'lessons': lesson_xp,
                'streaks': streak_xp,
                'boss_battles': boss_xp,
                'level_bonuses': level_bonus_xp,
            }
        })


class ChildAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsParentOfChild]

    def get(self, request, id):
        child = get_object_or_404(ChildProfile, id=id, parent=request.user)

        # Activity timestamps
        first_activity = ActivityLog.objects.filter(child=child).order_by('created_at').first()
        last_activity = ActivityLog.objects.filter(child=child).order_by('-created_at').first()

        # Mission stats
        from missions.models import Mission, MissionProgress
        total_missions = Mission.objects.filter(is_active=True).count()
        completed_missions = MissionProgress.objects.filter(child=child, status='completed').count()
        in_progress = MissionProgress.objects.filter(child=child, status='in_progress').count()

        # Lesson stats
        from academy.models import Lesson, LessonProgress
        total_lessons = Lesson.objects.count()
        completed_lessons = LessonProgress.objects.filter(child=child, completed=True).count()

        # Skill mastery (per character)
        from characters.models import Character
        skills = {}
        for character in Character.objects.all():
            char_missions = Mission.objects.filter(character=character, is_active=True).count()
            char_completed = MissionProgress.objects.filter(
                child=child, mission__character=character, status='completed'
            ).count()
            skills[character.slug] = {
                'name': character.name,
                'total': char_missions,
                'completed': char_completed,
                'mastery': round((char_completed / char_missions * 100) if char_missions > 0 else 0),
            }

        # Weekly activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        weekly_activity = (
            ActivityLog.objects.filter(child=child, created_at__gte=week_ago)
            .values('created_at__date')
            .annotate(count=Count('id'), xp=Sum('xp_earned'))
            .order_by('created_at__date')
        )

        # Badge progress
        total_badges = Badge.objects.count()
        earned_badges = EarnedBadge.objects.filter(child=child).count()

        current_rank = get_current_rank(child)

        return Response({
            'overview': {
                'xp': child.xp,
                'level': child.level,
                'streak': child.streak,
                'rank': RankSerializer(current_rank).data if current_rank else None,
                'member_since': first_activity.created_at if first_activity else child.joined_at,
                'last_active': last_activity.created_at if last_activity else None,
            },
            'missions': {
                'total': total_missions,
                'completed': completed_missions,
                'in_progress': in_progress,
                'completion_rate': round((completed_missions / total_missions * 100) if total_missions > 0 else 0),
            },
            'lessons': {
                'total': total_lessons,
                'completed': completed_lessons,
                'completion_rate': round((completed_lessons / total_lessons * 100) if total_lessons > 0 else 0),
            },
            'skills': skills,
            'badges': {
                'total': total_badges,
                'earned': earned_badges,
            },
            'weekly_activity': list(weekly_activity),
            'screen_time': {
                'limit_minutes': child.screen_time_limit_minutes,
            },
        })


class ChildActivityTimelineView(generics.ListAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsParentOfChild]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        child = get_object_or_404(ChildProfile, id=self.kwargs['id'], parent=self.request.user)
        queryset = ActivityLog.objects.filter(child=child).order_by('-created_at')

        activity_type = self.request.query_params.get('type')
        if activity_type:
            queryset = queryset.filter(type=activity_type)

        days = self.request.query_params.get('days')
        if days:
            cutoff = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(created_at__gte=cutoff)

        return queryset


class PilotDataExportView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsParent]

    def get(self, request):
        from missions.models import MissionProgress
        from academy.models import LessonProgress

        children = ChildProfile.objects.filter(parent=request.user)
        export = []
        for child in children:
            export.append({
                'child_id': str(child.id)[:8],
                'avatar': child.avatar_character,
                'level': child.level,
                'xp': child.xp,
                'streak_best': child.streak,
                'missions_completed': MissionProgress.objects.filter(child=child, status='completed').count(),
                'lessons_completed': LessonProgress.objects.filter(child=child, completed=True).count(),
                'badges_earned': EarnedBadge.objects.filter(child=child).count(),
                'days_active': ActivityLog.objects.filter(child=child).dates('created_at', 'day').count(),
                'total_xp_earned': ActivityLog.objects.filter(child=child).aggregate(total=Sum('xp_earned'))['total'] or 0,
                'rank': get_current_rank(child).name if get_current_rank(child) else 'Unranked',
            })

        return Response({
            'export_date': timezone.now().isoformat(),
            'total_children': len(export),
            'children': export,
        })
