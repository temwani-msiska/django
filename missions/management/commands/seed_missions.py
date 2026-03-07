from django.core.management.base import BaseCommand

from characters.models import Character
from missions.models import Mission, MissionReward, MissionStep
from rewards.models import Badge


# Rich step data for first 3 missions (World 1 / Byte missions 1-3)
MISSION_STEPS = {
    'byte-1': [
        {
            'num': 1, 'step_type': 'story', 'title': 'Welcome, SHERO!',
            'description': 'Meet Byte and learn about your mission.',
            'content': {'dialogue': [
                {'character': 'byte', 'text': 'Welcome, SHERO! I am Byte, your coding guide.'},
                {'character': 'byte', 'text': 'The internet is glitching and we need your help to fix it!'},
                {'character': 'narrator', 'text': 'Your first task: learn the basics of HTML.'},
            ]},
        },
        {
            'num': 2, 'step_type': 'multiple_choice', 'title': 'HTML Basics Quiz',
            'description': 'Answer a question about HTML.',
            'content': {
                'question': 'What does HTML stand for?',
                'options': ['Hyper Text Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyper Transfer Markup Language'],
                'correct_index': 0,
            },
        },
        {
            'num': 3, 'step_type': 'speech_bubble_fill', 'title': 'Byte Needs Your Help',
            'description': 'Fill in the blank to help Byte.',
            'content': {
                'character': 'byte',
                'template': 'To create a heading, we use the ___ tag.',
                'answer': 'h1',
                'case_sensitive': False,
            },
        },
        {
            'num': 4, 'step_type': 'code_editor_challenge', 'title': 'Write Your First Tag',
            'description': 'Write an HTML heading tag.',
            'content': {
                'prompt': 'Write an <h1> tag that says "Hello SHERO!"',
                'starter_code': '',
                'language': 'html',
                'validation': {'mode': 'contains', 'expected': '<h1>'},
            },
        },
        {
            'num': 5, 'step_type': 'true_false', 'title': 'True or False',
            'description': 'Test your knowledge.',
            'content': {
                'statement': 'HTML tags always need a closing tag.',
                'correct_answer': False,
            },
        },
        {
            'num': 6, 'step_type': 'story', 'title': 'Mission Complete!',
            'description': 'Byte congratulates you.',
            'content': {'dialogue': [
                {'character': 'byte', 'text': 'Amazing work, SHERO! You fixed the first glitch!'},
                {'character': 'narrator', 'text': 'You earned your first coding badge!'},
            ]},
        },
    ],
    'byte-2': [
        {
            'num': 1, 'step_type': 'story', 'title': 'The Next Glitch',
            'description': 'Byte has found another problem.',
            'content': {'dialogue': [
                {'character': 'byte', 'text': 'Great to see you again! There is another glitch in the system.'},
                {'character': 'byte', 'text': 'This time we need to learn about paragraphs and links.'},
            ]},
        },
        {
            'num': 2, 'step_type': 'drag_and_drop', 'title': 'Order the Tags',
            'description': 'Put the HTML tags in the correct order.',
            'content': {
                'prompt': 'Drag the tags into the correct order to build a webpage.',
                'items': ['<html>', '<head>', '<body>', '</body>', '</html>'],
                'correct_order': [0, 1, 2, 3, 4],
            },
        },
        {
            'num': 3, 'step_type': 'code_editor_challenge', 'title': 'Add a Paragraph',
            'description': 'Write a paragraph tag.',
            'content': {
                'prompt': 'Add a <p> tag with the text "I love coding!"',
                'starter_code': '<h1>My Page</h1>\n',
                'language': 'html',
                'validation': {'mode': 'contains', 'expected': '<p>'},
            },
        },
        {
            'num': 4, 'step_type': 'matching', 'title': 'Match the Tags',
            'description': 'Match each HTML tag to its purpose.',
            'content': {
                'prompt': 'Match each HTML tag to its purpose.',
                'pairs': [
                    {'left': '<h1>', 'right': 'Main heading'},
                    {'left': '<p>', 'right': 'Paragraph'},
                    {'left': '<a>', 'right': 'Link'},
                ],
            },
        },
        {
            'num': 5, 'step_type': 'debug_task', 'title': 'Fix the Link',
            'description': 'Find and fix the bug in the link tag.',
            'content': {
                'prompt': 'Fix the broken link tag!',
                'buggy_code': '<a href="https://example.com">Click here</p>',
                'language': 'html',
                'validation': {'mode': 'contains', 'expected': '</a>'},
            },
        },
        {
            'num': 6, 'step_type': 'mini_project', 'title': 'Build a Mini Page',
            'description': 'Create a page with heading, paragraph, and link.',
            'content': {
                'prompt': 'Build a page with a heading, paragraph, and a link.',
                'starter_code': '',
                'language': 'html',
                'validation': {'mode': 'contains_all', 'expected': ['<h1>', '<p>', '<a']},
            },
        },
        {
            'num': 7, 'step_type': 'story', 'title': 'Glitch Fixed!',
            'description': 'Byte celebrates your success.',
            'content': {'dialogue': [
                {'character': 'byte', 'text': 'You did it again! The second glitch is fixed!'},
            ]},
        },
    ],
    'byte-3': [
        {
            'num': 1, 'step_type': 'story', 'title': 'A Bigger Challenge',
            'description': 'Byte introduces a tougher mission.',
            'content': {'dialogue': [
                {'character': 'byte', 'text': 'SHERO, this glitch is bigger than the others.'},
                {'character': 'byte', 'text': 'We need to learn about lists and images to fix it!'},
            ]},
        },
        {
            'num': 2, 'step_type': 'multiple_choice', 'title': 'List Tags',
            'description': 'Test your knowledge of list tags.',
            'content': {
                'question': 'Which tag creates an unordered (bullet) list?',
                'options': ['<ul>', '<ol>', '<li>', '<list>'],
                'correct_index': 0,
            },
        },
        {
            'num': 3, 'step_type': 'command_sequence', 'title': 'Build a List',
            'description': 'Arrange the tags to create a list.',
            'content': {
                'prompt': 'Arrange these tags in the correct order to build a list.',
                'commands': ['<ul>', '<li>Item 1</li>', '<li>Item 2</li>', '</ul>'],
                'correct_order': [0, 1, 2, 3],
            },
        },
        {
            'num': 4, 'step_type': 'code_editor_challenge', 'title': 'Create a List',
            'description': 'Write an unordered list with 3 items.',
            'content': {
                'prompt': 'Create an unordered list with at least 2 items.',
                'starter_code': '',
                'language': 'html',
                'validation': {'mode': 'contains_all', 'expected': ['<ul>', '<li>', '</li>', '</ul>']},
            },
        },
        {
            'num': 5, 'step_type': 'speech_bubble_fill', 'title': 'Image Tag Help',
            'description': 'Help Byte remember the image tag.',
            'content': {
                'character': 'byte',
                'template': 'To add an image, we use the ___ tag.',
                'answer': 'img',
                'case_sensitive': False,
            },
        },
        {
            'num': 6, 'step_type': 'boss_battle_phase', 'title': 'Boss Battle: Fix the Page!',
            'description': 'Fix the corrupted HTML page.',
            'content': {
                'phase_number': 1,
                'leader': 'byte',
                'prompt': 'Fix the corrupted HTML! The list is broken.',
                'buggy_code': '<ul><li>Item 1<li>Item 2</ul>',
                'language': 'html',
                'validation': {'mode': 'contains', 'expected': '</li>'},
            },
        },
        {
            'num': 7, 'step_type': 'mini_project', 'title': 'Build a Fact Page',
            'description': 'Create a page about Zambia with a list and image tag.',
            'content': {
                'prompt': 'Build a Zambia fact page with a heading, list, and image tag.',
                'starter_code': '',
                'language': 'html',
                'validation': {'mode': 'contains_all', 'expected': ['<h1>', '<ul>', '<img']},
            },
        },
        {
            'num': 8, 'step_type': 'story', 'title': 'Victory!',
            'description': 'Byte awards you a special badge.',
            'content': {'dialogue': [
                {'character': 'byte', 'text': 'Incredible work, SHERO! You have earned the HTML Explorer badge!'},
                {'character': 'narrator', 'text': 'The third glitch is repaired. The internet is getting stronger!'},
            ]},
        },
    ],
}


class Command(BaseCommand):
    help = 'Seed all missions (18 total) with rich step types'

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

                # Use rich step data for first 3 missions, fallback for the rest
                if mission_id in MISSION_STEPS:
                    for step_data in MISSION_STEPS[mission_id]:
                        MissionStep.objects.create(
                            mission=mission,
                            num=step_data['num'],
                            step_type=step_data['step_type'],
                            title=step_data['title'],
                            description=step_data.get('description', ''),
                            hint=step_data.get('hint', ''),
                            content=step_data.get('content', {}),
                            validation_type=step_data.get('validation_type', ''),
                            validation_value=step_data.get('validation_value', ''),
                        )
                        step_count += 1
                else:
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
