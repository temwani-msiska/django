from django.core.management.base import BaseCommand

from characters.models import Character, CharacterAbility, CharacterStat


class Command(BaseCommand):
    help = 'Seed SHERO characters with abilities and stats'

    def handle(self, *args, **options):
        seeds = [
            {
                'slug': 'byte',
                'name': 'Byte',
                'title': 'The Problem Solver',
                'description': 'Debugs with joy',
                'backstory': 'Byte helps girls code.',
                'quote': 'Every bug has a clue!',
                'primary_color': '#6C5CE7',
                'secondary_color': '#A29BFE',
                'bg_color': '#F3F0FF',
                'order': 1,
                'abilities': [
                    ('🧠', 'Debug Vision', 'Can spot bugs quickly.'),
                    ('🔍', 'Logic Scan', 'Breaks problems into tiny steps.'),
                    ('🛠️', 'Fix Burst', 'Applies precise fixes.'),
                ],
                'stats': [('Logic', 92), ('Creativity', 78), ('Speed', 74)],
            },
            {
                'slug': 'pixel',
                'name': 'Pixel',
                'title': 'The Creative Builder',
                'description': 'Design and logic',
                'backstory': 'Pixel paints with code.',
                'quote': 'Create it one line at a time!',
                'primary_color': '#00B894',
                'secondary_color': '#55EFC4',
                'bg_color': '#E8FFF7',
                'order': 2,
                'abilities': [
                    ('🎨', 'Style Sense', 'Makes interfaces beautiful.'),
                    ('🧱', 'Layout Mastery', 'Builds clean structures.'),
                    ('🌈', 'Theme Shift', 'Adapts visuals quickly.'),
                ],
                'stats': [('Logic', 75), ('Creativity', 95), ('Speed', 72)],
            },
            {
                'slug': 'nova',
                'name': 'Nova',
                'title': 'The Future Coder',
                'description': 'Dreams big in tech',
                'backstory': 'Nova explores new worlds.',
                'quote': 'Your ideas can change the world!',
                'primary_color': '#0984E3',
                'secondary_color': '#74B9FF',
                'bg_color': '#EAF5FF',
                'order': 3,
                'abilities': [
                    ('🚀', 'Launch Plan', 'Turns ideas into projects.'),
                    ('🛰️', 'Future Sight', 'Thinks ahead in systems.'),
                    ('⚡', 'Energy Pulse', 'Keeps momentum high.'),
                ],
                'stats': [('Logic', 84), ('Creativity', 88), ('Speed', 86)],
            },
        ]

        for data in seeds:
            abilities = data.pop('abilities')
            stats = data.pop('stats')
            character, _ = Character.objects.update_or_create(slug=data['slug'], defaults=data)

            CharacterAbility.objects.filter(character=character).delete()
            for emoji, title, description in abilities:
                CharacterAbility.objects.create(character=character, emoji=emoji, title=title, description=description)

            CharacterStat.objects.filter(character=character).delete()
            for label, value in stats:
                CharacterStat.objects.create(character=character, label=label, value=value)

        self.stdout.write(self.style.SUCCESS('Characters seeded (3) with abilities and stats'))
