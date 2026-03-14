from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from academy.models import Lesson, LessonProgress, LessonStepProgress
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
from missions.models import Mission, MissionProgress
from rewards.models import ActivityLog, EarnedBadge

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


class JourneyStateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        child = get_child_from_request(request)

        # Count completed missions and lessons
        completed_missions = MissionProgress.objects.filter(
            child=child, status='completed'
        ).count()
        in_progress_missions = MissionProgress.objects.filter(
            child=child, status='in_progress'
        )
        completed_lessons = LessonProgress.objects.filter(
            child=child, completed=True
        ).count()

        # Find next available mission — exclude already-completed ones
        completed_mission_ids = MissionProgress.objects.filter(
            child=child, status='completed'
        ).values_list('mission_id', flat=True)
        available_missions = Mission.objects.filter(
            is_active=True
        ).exclude(id__in=completed_mission_ids).order_by('num')

        # Prefer in-progress mission, fall back to next available
        in_progress = in_progress_missions.select_related('mission').first()
        next_mission = in_progress.mission if in_progress else available_missions.first()

        # Find current/next lesson — prefer one with an active step
        current_lesson = None
        in_progress_step = LessonStepProgress.objects.filter(
            child=child, status='active'
        ).select_related('step__lesson').first()
        if in_progress_step:
            current_lesson = in_progress_step.step.lesson

        if not current_lesson:
            completed_lesson_ids = LessonProgress.objects.filter(
                child=child, completed=True
            ).values_list('lesson_id', flat=True)
            current_lesson = Lesson.objects.exclude(
                id__in=completed_lesson_ids
            ).order_by('track__order', 'order').first()

        # Determine current step number within the lesson
        current_step_number = None
        total_steps = 0
        if current_lesson:
            last_completed = LessonStepProgress.objects.filter(
                child=child,
                step__lesson=current_lesson,
                status='completed'
            ).order_by('-step__number').first()
            current_step_number = (last_completed.step.number + 1) if last_completed else 1
            total_steps = current_lesson.steps.count()

        # Determine journey state
        if completed_missions == 0 and completed_lessons == 0:
            state = 'brand_new'
        elif completed_lessons < 2 and completed_missions == 0:
            state = 'needs_first_lesson'
        elif completed_lessons >= 2 and completed_missions == 0:
            state = 'ready_for_missions'
        elif 0 < completed_missions < 9:
            state = 'between_missions'
        elif completed_missions == 9:
            state = 'boss_ready'
        elif completed_missions >= 10:
            state = 'world_complete'
        else:
            state = 'learning'

        # Build base response
        response_data = {
            'state': state,
            'completedMissions': completed_missions,
            'completedLessons': completed_lessons,
            'totalMissions': Mission.objects.filter(is_active=True).count(),
            'totalLessons': Lesson.objects.count(),
        }

        # Add next mission info
        if next_mission:
            response_data['nextMission'] = {
                'slug': next_mission.id,
                'title': next_mission.title,
                'description': next_mission.description,
                'characterSlug': next_mission.character.slug if next_mission.character else 'byte',
                'num': next_mission.num,
                'isInProgress': in_progress is not None,
            }

        # Add current lesson info
        if current_lesson:
            response_data['currentLesson'] = {
                'slug': current_lesson.id,
                'title': current_lesson.title,
                'trackSlug': current_lesson.track.id if current_lesson.track else None,
                'trackTitle': current_lesson.track.title if current_lesson.track else None,
                'currentStep': current_step_number,
                'totalSteps': total_steps,
            }

        # Add recommended action based on state
        if state == 'brand_new':
            response_data['recommendedAction'] = {
                'type': 'academy',
                'label': 'Start Your Training',
                'description': "Begin with HTML Basics in Byte's Code Lab",
                'href': '/academy',
            }
        elif state == 'needs_first_lesson':
            response_data['recommendedAction'] = {
                'type': 'academy',
                'label': 'Continue Learning',
                'description': f'Continue: {current_lesson.title}' if current_lesson else 'Keep training!',
                'href': (
                    f'/academy/{current_lesson.track.id}/{current_lesson.id}'
                    if current_lesson and current_lesson.track else '/academy'
                ),
            }
        elif state == 'ready_for_missions':
            response_data['recommendedAction'] = {
                'type': 'mission',
                'label': 'Start First Mission',
                'description': next_mission.title if next_mission else 'Begin your adventure!',
                'href': f'/play/world-1/{next_mission.id}' if next_mission else '/play/world-1',
            }
        elif state in ('between_missions', 'learning'):
            if next_mission:
                label = 'Continue Mission' if in_progress is not None else 'Next Mission'
                response_data['recommendedAction'] = {
                    'type': 'mission',
                    'label': label,
                    'description': next_mission.title,
                    'href': f'/play/world-1/{next_mission.id}',
                }
            elif current_lesson:
                response_data['recommendedAction'] = {
                    'type': 'academy',
                    'label': 'Continue Learning',
                    'description': current_lesson.title,
                    'href': f'/academy/{current_lesson.track.id}/{current_lesson.id}',
                }
        elif state == 'boss_ready':
            response_data['recommendedAction'] = {
                'type': 'boss',
                'label': 'Face Dr. Glitch!',
                'description': 'The final battle awaits!',
                'href': '/play/world-1/save-the-internet',
            }
        elif state == 'world_complete':
            response_data['recommendedAction'] = {
                'type': 'explore',
                'label': 'Keep Exploring',
                'description': 'Train more in the Academy or replay missions!',
                'href': '/academy',
            }

        return Response(response_data)
