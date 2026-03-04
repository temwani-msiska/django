from django.core.management.base import BaseCommand

from rewards.models import Badge


class Command(BaseCommand):
    help = 'Seed all badges'

    def handle(self, *args, **options):
        badges = [
            ('badge-loop-fixer', 'Loop Fixer', 'Mastered loop logic', '🔁', 'common', 'General'),
            ('badge-debug-detective', 'Debug Detective', 'Found a tricky bug', '🕵️', 'rare', 'Byte'),
            ('badge-first-mission', 'First Mission', 'Completed your first mission', '🚀', 'common', 'General'),
            ('badge-streak-3', '3-Day Streak', 'Kept coding 3 days in a row', '🔥', 'common', 'General'),
            ('badge-streak-7', '7-Day Streak', 'A full week of coding', '🌟', 'rare', 'General'),
            ('badge-byte-brave', 'Byte Brave', 'Completed Byte mission chain', '🧠', 'rare', 'Byte'),
            ('badge-pixel-artist', 'Pixel Artist', 'Completed Pixel mission chain', '🎨', 'rare', 'Pixel'),
            ('badge-nova-navigator', 'Nova Navigator', 'Completed Nova mission chain', '🪐', 'rare', 'Nova'),
            ('badge-css-spark', 'CSS Spark', 'Styled your first page', '✨', 'common', 'General'),
            ('badge-js-jumper', 'JS Jumper', 'Passed JavaScript lessons', '⚡', 'common', 'General'),
            ('badge-logic-lion', 'Logic Lion', 'Mastered logic track basics', '🦁', 'common', 'General'),
            ('badge-champion', 'Code Champion', 'Completed 10 missions', '🏆', 'epic', 'General'),
            ('badge-mentor-friend', 'Mentor Friend', 'Used mentor tips consistently', '🤝', 'rare', 'General'),
            ('badge-speed-coder', 'Speed Coder', 'Completed mission under time estimate', '⏱️', 'epic', 'General'),
            ('badge-code-shero', 'Code SHERO', 'Reached top rank', '👑', 'legendary', 'General'),
        ]
        for badge_id, name, description, emoji, rarity, category in badges:
            Badge.objects.update_or_create(
                id=badge_id,
                defaults={
                    'name': name,
                    'description': description,
                    'emoji': emoji,
                    'rarity': rarity,
                    'category': category,
                },
            )
        self.stdout.write(self.style.SUCCESS(f'Badges seeded ({len(badges)})'))
