from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import get_child_from_request
from core.utils import get_current_rank, get_next_rank
from rewards.models import Badge, Rank
from rewards.serializers import BadgeSerializer, RankSerializer


class BadgeListView(generics.ListAPIView):
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Badge.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['child'] = get_child_from_request(self.request)
        return context


class RankListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from missions.models import MissionProgress

        child = get_child_from_request(request)
        ranks = Rank.objects.all().order_by('order')
        current = get_current_rank(child)
        completed_missions = MissionProgress.objects.filter(child=child, status='completed').count()

        data = []
        for rank in ranks:
            data.append({
                'slug': rank.slug,
                'name': rank.name,
                'title': rank.title,
                'emoji': rank.emoji,
                'color': rank.color,
                'min_missions': rank.min_missions,
                'is_current': rank == current,
                'is_achieved': completed_missions >= rank.min_missions,
                'missions_needed': max(0, rank.min_missions - completed_missions),
            })

        next_rank = get_next_rank(child)

        return Response({
            'current_rank': RankSerializer(current).data if current else None,
            'next_rank': {
                'rank': RankSerializer(next_rank['rank']).data,
                'missions_needed': next_rank['missions_needed'],
            } if next_rank else None,
            'all_ranks': data,
        })
