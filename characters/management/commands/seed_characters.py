from django.core.management.base import BaseCommand

from characters.models import Character


class Command(BaseCommand):
    help = 'Seed SHERO characters'

    def handle(self, *args, **options):
        seeds = [
            {'slug': 'byte', 'name': 'Byte', 'title': 'The Problem Solver', 'description': 'Debugs with joy', 'backstory': 'Byte helps girls code.', 'quote': 'Every bug has a clue!', 'primary_color': '#6C5CE7', 'secondary_color': '#A29BFE', 'bg_color': '#F3F0FF', 'order': 1},
            {'slug': 'pixel', 'name': 'Pixel', 'title': 'The Creative Builder', 'description': 'Design and logic', 'backstory': 'Pixel paints with code.', 'quote': 'Create it one line at a time!', 'primary_color': '#00B894', 'secondary_color': '#55EFC4', 'bg_color': '#E8FFF7', 'order': 2},
            {'slug': 'nova', 'name': 'Nova', 'title': 'The Future Coder', 'description': 'Dreams big in tech', 'backstory': 'Nova explores new worlds.', 'quote': 'Your ideas can change the world!', 'primary_color': '#0984E3', 'secondary_color': '#74B9FF', 'bg_color': '#EAF5FF', 'order': 3},
        ]
        for data in seeds:
            Character.objects.update_or_create(slug=data['slug'], defaults=data)
        self.stdout.write(self.style.SUCCESS('Characters seeded'))
