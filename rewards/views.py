from rest_framework import generics, permissions

from core.authentication import get_child_from_request
from rewards.models import Badge
from rewards.serializers import BadgeSerializer


class BadgeListView(generics.ListAPIView):
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Badge.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['child'] = get_child_from_request(self.request)
        return context
