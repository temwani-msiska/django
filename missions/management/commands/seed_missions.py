from django.core.management.base import BaseCommand

from characters.models import Character
from missions.models import Mission, MissionReward, MissionStep
from rewards.models import Badge


class Command(BaseCommand):
    help = 'Seed all missions (18 total, 4 steps each)'

    def handle(self, *args, **options):
        characters = [Character.objects.get(slug='byte'), Character.objects.get(slug='pixel'), Character.objects.get(slug='nova')]
        languages = ['javascript', 'html', 'css']

        previous = None
        mission_count = 0
        step_count = 0

        for c_index, character in enumerate(characters):
            for num in range(1, 7):
                mission_id = f'{character.slug}-{num}'
                language = languages[(num - 1) % len(languages)]
                mission, _ = Mission.objects.update_or_create(
                    id=mission_id,
                    defaults={
                        'num': (c_index * 6) + num,
                        'title': f'{character.name} Mission {num}',
                        'description': f'{character.name} guided challenge {num}.',
                        'long_description': f'{character.name} welcomes you to mission {num}.',
                        'character': character,
                        'difficulty': 'Beginner' if num <= 2 else ('Intermediate' if num <= 4 else 'Advanced'),
                        'xp': 80 + (num * 20),
                        'coins': 10 + (num * 5),
                        'skills': ['Loops', 'Debugging'] if language == 'javascript' else ['Structure', 'Styling'],
                        'mentor_tip': 'Break down the task into tiny steps.',
                        'why_learn_this': 'This skill helps you solve real-world coding problems.',
                        'estimated_minutes': 8 + (num * 2),
                        'starter_code': 'console.log("Start coding");' if language == 'javascript' else ('<h1>Start coding</h1>' if language == 'html' else 'h1 { color: purple; }'),
                        'language': language,
                        'unlock_after': previous,
                        'is_active': True,
                    },
                )
                previous = mission
                mission_count += 1

                MissionStep.objects.filter(mission=mission).delete()
                for step_num in range(1, 5):
                    MissionStep.objects.create(
                        mission=mission,
                        num=step_num,
                        title=f'Step {step_num}',
                        description=f'Complete task step {step_num} for {mission.title}.',
                        hint='Try reading the example carefully.' if step_num > 1 else '',
                        validation_type='output_match' if language == 'javascript' else 'pattern_match',
                        validation_value='Hello SHERO' if language == 'javascript' else 'h1',
                    )
                    step_count += 1

                MissionReward.objects.filter(mission=mission).delete()
                MissionReward.objects.create(mission=mission, type='xp', label='XP Reward', value=mission.xp)
                MissionReward.objects.create(mission=mission, type='coins', label='Coin Reward', value=mission.coins)

                if num in (3, 6):
                    badge = Badge.objects.filter(category__in=[character.name, character.slug.title(), 'General']).first()
                    if badge:
                        MissionReward.objects.create(mission=mission, type='badge', label=badge.name, value=1, badge=badge)

        self.stdout.write(self.style.SUCCESS(f'Missions seeded ({mission_count}) with steps ({step_count})'))
