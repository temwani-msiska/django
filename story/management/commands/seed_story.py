from django.core.management.base import BaseCommand

from missions.models import Mission, MissionReward
from rewards.models import Badge
from story.models import Scene, StoryArc


class Command(BaseCommand):
    help = 'Seed story arcs, scenes, and link to missions'

    def handle(self, *args, **options):
        # ── Badge: First SHERO ──────────────────────────────────
        first_badge, _ = Badge.objects.update_or_create(
            id='badge-first-shero',
            defaults={
                'name': 'First SHERO',
                'description': 'Completed your very first SHERO mission!',
                'emoji': '🌟',
                'rarity': 'common',
                'category': 'General',
            },
        )
        self.stdout.write(self.style.SUCCESS('Badge "First SHERO" seeded'))

        # ── Arc 1: Prologue — The Rise of Dr. Glitch ───────────
        prologue, _ = StoryArc.objects.update_or_create(
            id='prologue-dr-glitch',
            defaults={
                'title': 'The Rise of Dr. Glitch',
                'description': 'Something strange is happening in Code City. Screens are glitching, robots are freezing, and nobody knows why…',
                'arc_type': 'prologue',
                'order': 1,
                'is_active': True,
            },
        )
        Scene.objects.filter(arc=prologue).delete()

        prologue_scenes = [
            {
                'order': 1,
                'title': 'Code City at Peace',
                'background_key': 'bg-code-city-day',
                'characters_on_screen': [
                    {'assetKey': 'citizens-idle', 'position': 'center', 'motion': 'fade-in'},
                ],
                'bubbles': [
                    {'speaker': 'narrator', 'text': 'Welcome to Code City — a place where everything runs on code.', 'type': 'narration'},
                    {'speaker': 'narrator', 'text': 'The robots help, the lights glow, and the screens always smile.', 'type': 'narration'},
                ],
                'motions': [],
                'music_key': 'music-peaceful-city',
                'sfx_keys': ['sfx-birds', 'sfx-soft-hum'],
                'next_action': 'next',
            },
            {
                'order': 2,
                'title': 'The Glitch Begins',
                'background_key': 'bg-code-city-glitch',
                'characters_on_screen': [
                    {'assetKey': 'screen-cracked', 'position': 'center', 'motion': 'shake'},
                ],
                'bubbles': [
                    {'speaker': 'narrator', 'text': 'But one day… the screens started flickering.', 'type': 'narration'},
                    {'speaker': 'narrator', 'text': 'Robots froze mid-step. Lights went dark.', 'type': 'narration'},
                ],
                'motions': [
                    {'target': 'screen', 'effect': 'shake', 'duration': 600},
                    {'target': 'screen', 'effect': 'flicker', 'duration': 400},
                ],
                'music_key': 'music-tension',
                'sfx_keys': ['sfx-glitch', 'sfx-static'],
                'next_action': 'next',
            },
            {
                'order': 3,
                'title': 'Dr. Glitch Appears',
                'background_key': 'bg-code-city-dark',
                'characters_on_screen': [
                    {'assetKey': 'dr-glitch-reveal', 'position': 'center', 'motion': 'zoom-in'},
                ],
                'bubbles': [
                    {'speaker': 'dr-glitch', 'text': 'Ha ha ha! I am Dr. Glitch!', 'type': 'speech'},
                    {'speaker': 'dr-glitch', 'text': 'I have scrambled every line of code in this city. No one can stop me!', 'type': 'speech'},
                ],
                'motions': [
                    {'target': 'screen', 'effect': 'shake', 'duration': 300},
                ],
                'music_key': 'music-villain-theme',
                'sfx_keys': ['sfx-evil-laugh', 'sfx-thunder'],
                'next_action': 'next',
            },
            {
                'order': 4,
                'title': 'The City Needs a Hero',
                'background_key': 'bg-code-city-dark',
                'characters_on_screen': [
                    {'assetKey': 'citizens-worried', 'position': 'left', 'motion': 'fade-in'},
                    {'assetKey': 'elder-bot', 'position': 'right', 'motion': 'slide-in-right'},
                ],
                'bubbles': [
                    {'speaker': 'elder-bot', 'text': 'There is only one way to fix this…', 'type': 'speech'},
                    {'speaker': 'elder-bot', 'text': 'We need someone who can learn to CODE.', 'type': 'speech'},
                    {'speaker': 'elder-bot', 'text': 'We need… a SHERO.', 'type': 'speech'},
                ],
                'motions': [],
                'music_key': 'music-hopeful',
                'sfx_keys': ['sfx-whoosh'],
                'next_action': 'next',
            },
            {
                'order': 5,
                'title': 'That SHERO Is You',
                'background_key': 'bg-spotlight',
                'characters_on_screen': [
                    {'assetKey': 'byte-pose', 'position': 'left', 'motion': 'slide-in-left'},
                    {'assetKey': 'pixel-pose', 'position': 'center', 'motion': 'fade-in'},
                    {'assetKey': 'nova-pose', 'position': 'right', 'motion': 'slide-in-right'},
                ],
                'bubbles': [
                    {'speaker': 'narrator', 'text': 'That SHERO… is YOU.', 'type': 'narration'},
                    {'speaker': 'narrator', 'text': 'Choose your avatar and begin your coding adventure!', 'type': 'narration'},
                ],
                'motions': [
                    {'target': 'screen', 'effect': 'glow', 'duration': 1000},
                ],
                'music_key': 'music-hero-theme',
                'sfx_keys': ['sfx-sparkle', 'sfx-whoosh'],
                'next_action': 'end',
            },
        ]

        for s in prologue_scenes:
            Scene.objects.create(arc=prologue, **s)
        self.stdout.write(self.style.SUCCESS(f'Prologue arc seeded ({len(prologue_scenes)} scenes)'))

        # ── Arc 2: Mission 1 Intro — Welcome SHERO ─────────────
        m1_intro, _ = StoryArc.objects.update_or_create(
            id='mission-1-intro',
            defaults={
                'title': 'Welcome SHERO',
                'description': 'Your first mission begins! Learn what code is and help a robot wake up.',
                'arc_type': 'mission_intro',
                'order': 2,
                'is_active': True,
            },
        )
        Scene.objects.filter(arc=m1_intro).delete()

        m1_scenes = [
            {
                'order': 1,
                'title': 'What Is Code?',
                'background_key': 'bg-classroom',
                'characters_on_screen': [
                    {'assetKey': 'mentor-bot', 'position': 'right', 'motion': 'slide-in-right'},
                ],
                'bubbles': [
                    {'speaker': 'mentor-bot', 'text': 'Code is a set of instructions that tells a computer what to do.', 'type': 'speech'},
                    {'speaker': 'mentor-bot', 'text': 'Just like a recipe tells you how to bake a cake!', 'type': 'speech'},
                ],
                'motions': [],
                'music_key': 'music-learning',
                'sfx_keys': ['sfx-chime'],
                'next_action': 'next',
            },
            {
                'order': 2,
                'title': 'Code Makes Things Happen',
                'background_key': 'bg-classroom',
                'characters_on_screen': [
                    {'assetKey': 'mentor-bot', 'position': 'right', 'motion': 'idle'},
                    {'assetKey': 'lightbulb-off', 'position': 'center', 'motion': 'fade-in'},
                ],
                'bubbles': [
                    {'speaker': 'mentor-bot', 'text': 'Watch this! When I run this code…', 'type': 'speech'},
                    {'speaker': 'mentor-bot', 'text': 'turnOn("light")', 'type': 'code'},
                    {'speaker': 'narrator', 'text': '💡 The light turns on!', 'type': 'narration'},
                ],
                'motions': [
                    {'target': 'lightbulb-off', 'effect': 'swap', 'swapTo': 'lightbulb-on', 'duration': 500},
                ],
                'music_key': 'music-learning',
                'sfx_keys': ['sfx-typing', 'sfx-power-on'],
                'next_action': 'next',
            },
            {
                'order': 3,
                'title': 'A Sleeping Robot',
                'background_key': 'bg-workshop',
                'characters_on_screen': [
                    {'assetKey': 'robot-sleeping', 'position': 'center', 'motion': 'fade-in'},
                    {'assetKey': 'mentor-bot', 'position': 'right', 'motion': 'idle'},
                ],
                'bubbles': [
                    {'speaker': 'mentor-bot', 'text': 'Oh no! This little robot has fallen asleep.', 'type': 'speech'},
                    {'speaker': 'mentor-bot', 'text': 'It needs code to wake up. Can you help?', 'type': 'speech'},
                ],
                'motions': [],
                'music_key': 'music-curious',
                'sfx_keys': ['sfx-robot-snore'],
                'next_action': 'next',
            },
            {
                'order': 4,
                'title': 'Your First Code',
                'background_key': 'bg-workshop',
                'characters_on_screen': [
                    {'assetKey': 'robot-sleeping', 'position': 'center', 'motion': 'idle'},
                    {'assetKey': 'code-editor', 'position': 'bottom', 'motion': 'slide-up'},
                ],
                'bubbles': [
                    {'speaker': 'mentor-bot', 'text': 'Press the "Run Code" button to wake up the robot!', 'type': 'speech'},
                ],
                'motions': [],
                'music_key': 'music-curious',
                'sfx_keys': [],
                'next_action': 'run_code',
                'action_payload': {
                    'starterCode': 'wakeUp(robot)',
                    'language': 'pseudocode',
                    'successAsset': 'robot-awake',
                    'successSfx': 'sfx-robot-wake',
                },
            },
            {
                'order': 5,
                'title': 'Robot Awakens!',
                'background_key': 'bg-workshop',
                'characters_on_screen': [
                    {'assetKey': 'robot-awake', 'position': 'center', 'motion': 'bounce'},
                    {'assetKey': 'mentor-bot', 'position': 'right', 'motion': 'idle'},
                ],
                'bubbles': [
                    {'speaker': 'robot', 'text': 'Beep boop! Thank you, SHERO!', 'type': 'speech'},
                    {'speaker': 'mentor-bot', 'text': 'Amazing! You just ran your first code!', 'type': 'speech'},
                    {'speaker': 'mentor-bot', 'text': "You're ready for your first real mission.", 'type': 'speech'},
                ],
                'motions': [
                    {'target': 'screen', 'effect': 'confetti', 'duration': 2000},
                ],
                'music_key': 'music-celebration',
                'sfx_keys': ['sfx-robot-wake', 'sfx-sparkle', 'sfx-cheer'],
                'next_action': 'end',
            },
        ]

        for s in m1_scenes:
            Scene.objects.create(arc=m1_intro, **s)
        self.stdout.write(self.style.SUCCESS(f'Mission 1 intro arc seeded ({len(m1_scenes)} scenes)'))

        # ── Link Mission 1 to story arcs and badge ──────────────
        # Find the first mission (byte-1 from seed_missions, or num=1)
        mission1 = Mission.objects.filter(num=1).first()
        if mission1:
            mission1.intro_arc = m1_intro
            mission1.requires_arc = prologue
            mission1.save(update_fields=['intro_arc', 'requires_arc'])

            # Ensure the First SHERO badge is a reward
            MissionReward.objects.get_or_create(
                mission=mission1,
                type='badge',
                badge=first_badge,
                defaults={'label': first_badge.name, 'value': 1},
            )
            self.stdout.write(self.style.SUCCESS(f'Mission "{mission1.id}" linked to arcs and badge'))
        else:
            self.stdout.write(self.style.WARNING('No mission with num=1 found — skipping mission link'))

        self.stdout.write(self.style.SUCCESS('Story seeding complete!'))
