from django.core.management.base import BaseCommand

from rewards.models import Rank

RANKS = [
    {'slug': 'code-rookie', 'name': 'Code Rookie', 'title': 'Just Getting Started', 'emoji': '\U0001f331', 'min_missions': 0, 'color': '#94A3B8', 'order': 1},
    {'slug': 'code-cadet', 'name': 'Code Cadet', 'title': 'Learning the Basics', 'emoji': '\u2b50', 'min_missions': 3, 'color': '#60A5FA', 'order': 2},
    {'slug': 'code-explorer', 'name': 'Code Explorer', 'title': 'Discovering New Worlds', 'emoji': '\U0001f680', 'min_missions': 6, 'color': '#34D399', 'order': 3},
    {'slug': 'code-hero', 'name': 'Code Hero', 'title': 'Defending the Digital World', 'emoji': '\U0001f9b8', 'min_missions': 10, 'color': '#F59E0B', 'order': 4},
    {'slug': 'code-master', 'name': 'Code Master', 'title': 'Master of the Code', 'emoji': '\U0001f451', 'min_missions': 15, 'color': '#F97316', 'order': 5},
    {'slug': 'code-shero', 'name': 'Code SHERO', 'title': 'Ultimate Digital Hero', 'emoji': '\U0001f48e', 'min_missions': 20, 'color': '#7B2D8E', 'order': 6},
]


class Command(BaseCommand):
    help = 'Seed rank data'

    def handle(self, *args, **options):
        for rank_data in RANKS:
            Rank.objects.update_or_create(
                slug=rank_data['slug'],
                defaults=rank_data,
            )
        self.stdout.write(self.style.SUCCESS(f'Ranks seeded ({len(RANKS)})'))
