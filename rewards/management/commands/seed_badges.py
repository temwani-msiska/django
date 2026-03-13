from django.core.management.base import BaseCommand

from rewards.models import Badge


class Command(BaseCommand):
    help = 'Seed all badges'

    def handle(self, *args, **options):
        badges = [
            # Common badges
            ('badge-style-starter', 'Style Starter', 'Wrote your first CSS rule', '🎨', 'common', 'Pixel'),
            ('badge-robot-fixer', 'Robot Fixer', "Rebooted Nova's robot", '🤖', 'common', 'Nova'),
            ('badge-loop-fixer', 'Loop Fixer', 'Fixed your first broken loop', '🔄', 'common', 'Byte'),
            ('badge-first-mission', 'First Mission', 'Completed your very first mission', '⭐', 'common', 'General'),
            ('badge-streak-3', '3-Day Streak', 'Coded for 3 days in a row', '🔥', 'common', 'General'),

            # Rare badges
            ('badge-maze-master', 'Maze Master', 'Solved the If/Else Maze', '🧩', 'rare', 'Byte'),
            ('badge-flex-master', 'Flex Master', 'Mastered CSS Flexbox', '📏', 'rare', 'Pixel'),
            ('badge-data-wrangler', 'Data Wrangler', 'Sorted and filtered arrays', '📊', 'rare', 'Byte'),
            ('badge-data-scientist', 'Data Scientist', 'Collected and analysed experiment data', '🔬', 'rare', 'Nova'),
            ('badge-responsive-hero', 'Responsive Hero', 'Made a site work on all screens', '📱', 'rare', 'Pixel'),
            ('badge-signal-expert', 'Signal Expert', 'Encoded a secret satellite message', '📡', 'rare', 'Nova'),

            # Epic badges
            ('badge-bug-squasher', 'Bug Squasher', 'Squashed 10 Code Bugs', '🐛', 'epic', 'General'),

            # Legendary badges
            ('badge-logic-legend', 'Logic Legend', "Completed Byte's final challenge", '🏆', 'legendary', 'Byte'),
            ('badge-design-legend', 'Design Legend', "Completed Pixel's final challenge", '🏆', 'legendary', 'Pixel'),
            ('badge-discovery-legend', 'Discovery Legend', "Completed Nova's final challenge", '🏆', 'legendary', 'Nova'),

            # Streak badges
            ('streak-3-day', '3-Day Streak', '3-day streak milestone!', '🔥', 'common', 'streak'),
            ('streak-5-day', '5-Day Streak', '5-day streak milestone!', '🔥🔥', 'common', 'streak'),
            ('streak-7-day', 'Week Warrior', '7-day streak milestone!', '⚡', 'rare', 'streak'),
            ('streak-14-day', 'Two-Week Champion', '14-day streak milestone!', '💪', 'rare', 'streak'),
            ('streak-30-day', 'Monthly Master', '30-day streak milestone!', '🏆', 'epic', 'streak'),
            ('streak-60-day', 'Unstoppable', '60-day streak milestone!', '🌟', 'epic', 'streak'),
            ('streak-100-day', 'Legendary Streak', '100-day streak milestone!', '💎', 'legendary', 'streak'),
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
