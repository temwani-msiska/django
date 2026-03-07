from django.core.management.base import BaseCommand

from rewards.models import Badge


WORLD_1_BADGES = [
    {'id': 'first-code', 'name': 'First Code Runner', 'emoji': '🚀', 'rarity': 'common', 'category': 'mission', 'description': 'Ran your very first line of code!'},
    {'id': 'structure-builder', 'name': 'Structure Builder', 'emoji': '🏗️', 'rarity': 'common', 'category': 'mission', 'description': 'Rebuilt the HTML structure of a broken website!'},
    {'id': 'color-artist', 'name': 'Color Artist', 'emoji': '🎨', 'rarity': 'common', 'category': 'mission', 'description': 'Used CSS to bring color back to the digital world!'},
    {'id': 'page-builder', 'name': 'Page Builder', 'emoji': '📄', 'rarity': 'rare', 'category': 'mission', 'description': 'Built a complete webpage with headings and paragraphs!'},
    {'id': 'bug-squasher', 'name': 'Bug Squasher', 'emoji': '🐛', 'rarity': 'rare', 'category': 'mission', 'description': 'Found and fixed bugs in broken HTML code!'},
    {'id': 'logic-master', 'name': 'Logic Master', 'emoji': '🧠', 'rarity': 'rare', 'category': 'mission', 'description': 'Mastered logic commands to navigate the maze!'},
    {'id': 'web-designer', 'name': 'Web Designer', 'emoji': '✨', 'rarity': 'epic', 'category': 'mission', 'description': 'Built the SHERO HQ page using HTML and CSS together!'},
    {'id': 'world-1-champion', 'name': 'World 1 Champion', 'emoji': '🏆', 'rarity': 'legendary', 'category': 'world', 'description': 'Defeated Dr. Glitch and saved the internet! You are a true Code SHERO!'},
    {'id': 'boss-slayer', 'name': 'Boss Slayer', 'emoji': '⚔️', 'rarity': 'legendary', 'category': 'boss', 'description': 'Defeated Dr. Glitch in the Boss Battle!'},
    {'id': 'perfect-boss', 'name': 'Flawless Victory', 'emoji': '💎', 'rarity': 'legendary', 'category': 'boss', 'description': 'Defeated Dr. Glitch without failing a single phase!'},
]


class Command(BaseCommand):
    help = 'Seed World 1 badges'

    def handle(self, *args, **options):
        for badge in WORLD_1_BADGES:
            Badge.objects.update_or_create(
                id=badge['id'],
                defaults={
                    'name': badge['name'],
                    'emoji': badge['emoji'],
                    'rarity': badge['rarity'],
                    'category': badge['category'],
                    'description': badge['description'],
                },
            )
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(WORLD_1_BADGES)} World 1 badges.'))
