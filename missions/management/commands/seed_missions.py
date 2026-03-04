from django.core.management.base import BaseCommand

from characters.models import Character
from missions.models import Mission, MissionStep


class Command(BaseCommand):
    help = 'Seed missions'

    def handle(self, *args, **options):
        byte = Character.objects.get(slug='byte')
        mission, _ = Mission.objects.update_or_create(
            id='byte-1',
            defaults={
                'num': 1,
                'title': 'Hello Code',
                'description': 'Print your first output',
                'long_description': 'Byte welcomes you to Code SHEROs.',
                'character': byte,
                'difficulty': 'Beginner',
                'xp': 100,
                'coins': 10,
                'skills': ['Output'],
                'mentor_tip': 'Read the prompt carefully.',
                'why_learn_this': 'Output is foundational.',
                'estimated_minutes': 10,
                'starter_code': 'console.log(???);',
                'language': 'javascript',
            },
        )
        MissionStep.objects.update_or_create(
            mission=mission,
            num=1,
            defaults={
                'title': 'Write output',
                'description': 'Use console.log to print Hello SHERO',
                'validation_type': 'output_match',
                'validation_value': 'Hello SHERO',
            },
        )
        self.stdout.write(self.style.SUCCESS('Missions seeded'))
