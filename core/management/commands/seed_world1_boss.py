from django.core.management.base import BaseCommand

from characters.models import Character
from missions.models import BossBattle, BossBattlePhase, Mission
from story.models import StoryArc


class Command(BaseCommand):
    help = 'Seed World 1 boss battle for save-the-internet mission'

    def handle(self, *args, **options):
        try:
            byte = Character.objects.get(slug='byte')
            pixel = Character.objects.get(slug='pixel')
            nova = Character.objects.get(slug='nova')
        except Character.DoesNotExist:
            self.stdout.write(self.style.ERROR('Missing characters. Run seed_characters first.'))
            return

        try:
            mission = Mission.objects.get(id='save-the-internet')
            intro_arc = StoryArc.objects.get(id='boss-battle-intro')
            victory_arc = StoryArc.objects.get(id='boss-battle-victory')
        except (Mission.DoesNotExist, StoryArc.DoesNotExist):
            self.stdout.write(self.style.ERROR('Missing mission/arcs. Run seed_world1_story and seed_world1_missions first.'))
            return

        boss, _ = BossBattle.objects.update_or_create(
            mission=mission,
            defaults={
                'title': "Dr. Glitch's Final Stand",
                'description': 'The final showdown at the Digital Core! Defeat Dr. Glitch in three phases to restore the internet.',
                'total_phases': 3,
                'intro_arc': intro_arc,
                'victory_arc': victory_arc,
                'xp_bonus': 200,
                'defeat_dialogue': [
                    {'character': 'dr_glitch', 'text': 'Ha! Your code is no match for my bugs!', 'bubble_type': 'shout'},
                    {'character': 'byte', 'text': 'Don\'t give up, SHERO! We can do this!', 'bubble_type': 'speech'},
                    {'character': 'pixel', 'text': 'Let\'s try again — we\'re stronger together!', 'bubble_type': 'speech'},
                ],
            },
        )

        phases = [
            {
                'phase_number': 1,
                'leader_character': byte,
                'title': 'Phase 1: Rebuilding the Wall',
                'description': 'Dr. Glitch throws a Tag-Tornado that rips the headers off the Central Gateway!',
                'challenge_type': 'drag_and_drop',
                'content': {
                    'prompt': "Dr. Glitch's Tag-Tornado scattered the HTML! Drag the tags back into the correct order to rebuild the firewall!",
                    'items': ['<html>', '<head>', '<title>SHERO Shield</title>', '</head>', '<body>', '<h1>Central Gateway</h1>', '</body>', '</html>'],
                    'correct_order': [0, 1, 2, 3, 4, 5, 6, 7],
                },
                'intro_dialogue': [
                    {'character': 'byte', 'text': "He's trying to collapse the site!", 'bubble_type': 'speech'},
                    {'character': 'byte', 'text': 'I need to lock these HTML tags back into place. Quick, help me rebuild the structure!', 'bubble_type': 'speech'},
                ],
                'success_dialogue': [
                    {'character': 'byte', 'text': 'HTML structure restored!', 'bubble_type': 'speech'},
                    {'character': 'dr_glitch', 'text': "Lucky shot! But you'll never bring back the color!", 'bubble_type': 'shout'},
                    {'character': 'byte', 'text': "Pixel, you're up!", 'bubble_type': 'speech'},
                ],
            },
            {
                'phase_number': 2,
                'leader_character': pixel,
                'title': 'Phase 2: The Shield of Color',
                'description': 'Dr. Glitch launches Shadow Pixels that turn everything black and white!',
                'challenge_type': 'code_editor_challenge',
                'content': {
                    'prompt': 'Dr. Glitch turned everything grey! Use CSS to bring back the color. Set the background-color to #FF69B4 (Neon Pink) to blind him with style!',
                    'starter_code': '<style>\n  body {\n    /* Add the background-color here! */\n  }\n</style>\n<body>\n  <h1>SHERO Shield: ACTIVE</h1>\n  <p>The internet is fighting back!</p>\n</body>',
                    'language': 'html',
                    'validation': {'mode': 'contains_all', 'expected': ['background-color', '#FF69B4']},
                },
                'intro_dialogue': [
                    {'character': 'pixel', 'text': 'Everything is so gloomy!', 'bubble_type': 'speech'},
                    {'character': 'pixel', 'text': "If I can just inject some CSS energy, we can blast through these shadows. Let's go NEON PINK!", 'bubble_type': 'speech'},
                ],
                'success_dialogue': [
                    {'character': 'pixel', 'text': 'Color is BACK, baby!', 'bubble_type': 'shout'},
                    {'character': 'dr_glitch', 'text': 'My eyes! Too... much... PINK!', 'bubble_type': 'shout'},
                    {'character': 'pixel', 'text': 'Nova, finish him off!', 'bubble_type': 'speech'},
                ],
            },
            {
                'phase_number': 3,
                'leader_character': nova,
                'title': 'Phase 3: The Logic Trap',
                'description': 'Dr. Glitch tries to escape! Sequence the commands to activate the Gravity Beam!',
                'challenge_type': 'command_sequence',
                'content': {
                    'prompt': 'Dr. Glitch is escaping in his Glitch-Glider! Put the commands in the exact right order to activate the Gravity Beam and catch him!',
                    'commands': ['aim()', 'powerUp()', 'activateBeam()'],
                    'correct_order': [0, 1, 2],
                },
                'intro_dialogue': [
                    {'character': 'nova', 'text': "He's getting away!", 'bubble_type': 'speech'},
                    {'character': 'nova', 'text': "Robot Companion, standby! We need to aim, power up, and activate the beam. If we miss one step, he'll vanish into the dark web!", 'bubble_type': 'speech'},
                ],
                'success_dialogue': [
                    {'character': 'nova', 'text': 'GRAVITY BEAM: LOCKED ON!', 'bubble_type': 'shout'},
                    {'character': 'dr_glitch', 'text': "Curse you, Code SHEROs! You haven't seen the last of me! I still haven't taught you about... ARRAYS! Or DATABASES! I'll be back!", 'bubble_type': 'shout'},
                    {'character': 'byte', 'text': 'We did it... WE ACTUALLY DID IT!', 'bubble_type': 'shout'},
                    {'character': 'pixel', 'text': 'The internet is saved!', 'bubble_type': 'shout'},
                    {'character': 'nova', 'text': 'SHERO team for the WIN!', 'bubble_type': 'shout'},
                ],
            },
        ]

        for phase in phases:
            BossBattlePhase.objects.update_or_create(
                boss_battle=boss,
                phase_number=phase['phase_number'],
                defaults={
                    'leader_character': phase['leader_character'],
                    'title': phase['title'],
                    'description': phase['description'],
                    'challenge_type': phase['challenge_type'],
                    'content': phase['content'],
                    'intro_dialogue': phase['intro_dialogue'],
                    'success_dialogue': phase['success_dialogue'],
                    'health_bar_label': 'Dr. Glitch',
                },
            )

        BossBattlePhase.objects.filter(boss_battle=boss).exclude(phase_number__in=[1, 2, 3]).delete()
        self.stdout.write(self.style.SUCCESS('Seeded World 1 boss battle.'))
