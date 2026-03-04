from django.core.management.base import BaseCommand

from rewards.models import Badge


class Command(BaseCommand):
    help = 'Seed badges'

    def handle(self, *args, **options):
        badges = [
            ('badge-loop-fixer', 'Loop Fixer', 'Mastered loop logic', '🔁', 'common', 'General'),
            ('badge-debug-detective', 'Debug Detective', 'Found a tricky bug', '🕵️', 'rare', 'Byte'),
        ]
        for badge_id, name, description, emoji, rarity, category in badges:
            Badge.objects.update_or_create(id=badge_id, defaults={'name': name, 'description': description, 'emoji': emoji, 'rarity': rarity, 'category': category})
        self.stdout.write(self.style.SUCCESS('Badges seeded'))
