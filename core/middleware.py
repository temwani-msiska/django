from django.http import JsonResponse
from django.utils import timezone

from accounts.models import ChildProfile
from rewards.models import ActivityLog


class ScreenTimeMiddleware:
    """
    Checks if a child has exceeded their screen time limit.
    Returns 429 with time_remaining=0 if exceeded.
    Only applies to child-authenticated requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def _get_child_id_from_token(self, request):
        """Extract child_id from JWT token in Authorization header."""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        token_str = auth_header[7:]
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            token = AccessToken(token_str)
            return token.payload.get('child_id')
        except Exception:
            return None

    def __call__(self, request):
        child_id = self._get_child_id_from_token(request)
        if not child_id:
            return self.get_response(request)

        try:
            child = ChildProfile.objects.get(id=child_id)
        except ChildProfile.DoesNotExist:
            return self.get_response(request)

        if child.screen_time_limit_minutes is None or child.screen_time_limit_minutes == 0:
            return self.get_response(request)

        # Calculate time used today from activity logs
        today = timezone.now().date()
        today_activities = ActivityLog.objects.filter(
            child=child,
            created_at__date=today
        ).count()

        # Rough estimate: each activity ~ 3 minutes
        estimated_minutes = today_activities * 3

        if estimated_minutes >= child.screen_time_limit_minutes:
            return JsonResponse({
                'error': 'screen_time_exceeded',
                'message': 'You have reached your screen time limit for today! Come back tomorrow.',
                'time_limit': child.screen_time_limit_minutes,
                'time_used': estimated_minutes,
            }, status=429)

        response = self.get_response(request)
        response['X-Screen-Time-Limit'] = str(child.screen_time_limit_minutes)
        response['X-Screen-Time-Used'] = str(estimated_minutes)
        response['X-Screen-Time-Remaining'] = str(max(0, child.screen_time_limit_minutes - estimated_minutes))
        return response
