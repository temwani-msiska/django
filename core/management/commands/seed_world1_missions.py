from django.core.management.base import BaseCommand

from characters.models import Character
from missions.models import Mission, MissionReward, MissionStep
from rewards.models import Badge
from story.models import StoryArc


def step(num, step_type, title, description, content, hint=''):
    return {
        'num': num,
        'step_type': step_type,
        'title': title,
        'description': description,
        'hint': hint,
        'content': content,
    }


MISSION_DATA = [
    {
        'id': 'welcome-shero', 'title': 'Welcome SHERO',
        'description': 'A massive digital tremor shakes the network! Help Byte, Pixel, and Nova wake up the system by running your first code.',
        'character': 'byte', 'difficulty': 'Beginner', 'xp': 50, 'coins': 10,
        'skills': ['Introduction', 'Running Code'], 'language': 'html', 'num': 1,
        'intro_arc': 'mission-1-intro', 'outro_arc': 'mission-1-outro', 'requires_arc': 'world-1-prologue',
        'steps': [
            step(1, 'story', 'Wake the Gateway', 'Byte explains the situation.', {'dialogue': [{'character': 'byte', 'text': 'The Gateway Robot is powered down. We need to run some code to wake it up!'}]}),
            step(2, 'true_false', 'What Running Code Means', 'Answer true or false.', {'statement': 'Running code means telling the computer to execute your instructions.', 'correct_answer': True}),
            step(3, 'code_editor_challenge', 'Run to Wake', 'Press Run to wake the Gateway Robot!', {'prompt': 'Press Run to wake up the Gateway Robot!', 'starter_code': '<!-- Press the Run button! -->\n<h1>Wake up!</h1>', 'language': 'html', 'validation': {'mode': 'contains', 'expected': '<h1>'}}),
            step(4, 'story', 'Robot Online', 'Robot powers up.', {'dialogue': [{'character': 'byte', 'text': 'Yes! It worked!'}, {'character': 'pixel', 'text': 'The fog is clearing!'}, {'character': 'nova', 'text': 'Great first run, SHERO!'}]}),
        ],
        'rewards': [('xp', 'Mission XP', 50, None), ('badge', 'First Code Runner', 0, 'first-code')],
    },
    {
        'id': 'say-hello', 'title': 'Say Hello', 'description': "The Gateway Robot is awake but its speech chip is scrambled! Help Byte code an HTML header so the robot can say 'Hello SHERO!'", 'character': 'byte', 'difficulty': 'Beginner', 'xp': 75, 'coins': 15,
        'skills': ['HTML Headers', '<h1> Tag'], 'language': 'html', 'num': 2,
        'intro_arc': 'mission-2-intro', 'outro_arc': 'mission-2-outro',
        'steps': [
            step(1, 'story', 'Logic Goggles', 'Byte inspects the speech chip.', {'dialogue': [{'character': 'byte', 'text': 'I can see a garbled text layer in here!'}]}),
            step(2, 'multiple_choice', 'Biggest Heading', 'Pick the right tag.', {'question': 'Which HTML tag creates the biggest heading?', 'options': ['<h1>', '<p>', '<div>', '<span>'], 'correct_index': 0}),
            step(3, 'speech_bubble_fill', 'Complete the Tag', 'Fill in the blank.', {'character': 'byte', 'template': 'To create a heading, use the ___ tag.', 'answer': 'h1', 'case_sensitive': False}),
            step(4, 'code_editor_challenge', 'Make Robot Talk', 'Write the heading.', {'prompt': "Write an HTML heading that says 'Hello SHERO!'", 'starter_code': '', 'language': 'html', 'validation': {'mode': 'contains_all', 'expected': ['<h1>', 'Hello SHERO!']}}),
            step(5, 'story', 'Success', 'Robot greets SHERO.', {'dialogue': [{'character': 'narrator', 'text': 'The robot speaks clearly: Hello SHERO!'}, {'character': 'byte', 'text': 'Mission complete!'}]}),
        ],
        'rewards': [('xp', 'Mission XP', 75, None)],
    },
    {
        'id': 'fix-the-website', 'title': 'Fix the Website', 'description': 'Dr. Glitch knocked over all the building blocks! Help Byte rebuild the page structure.', 'character': 'byte', 'difficulty': 'Beginner', 'xp': 75, 'coins': 15,
        'skills': ['HTML Structure', '<title> Tag', 'Page Structure'], 'language': 'html', 'num': 3, 'intro_arc': 'mission-3-intro', 'outro_arc': 'mission-3-outro',
        'steps': [
            step(1, 'story', 'Scattered Blocks', 'Byte examines the site.', {'dialogue': [{'character': 'byte', 'text': 'The building blocks are out of order. Let’s rebuild from the top.'}]}),
            step(2, 'drag_and_drop', 'Reorder Tags', 'Drag in order.', {'prompt': 'Drag the HTML building blocks into the correct order.', 'items': ['<!DOCTYPE html>', '<html>', '<head>', '<title>Library of Info</title>', '</head>', '<body>', '</body>', '</html>'], 'correct_order': [0, 1, 2, 3, 4, 5, 6, 7]}),
            step(3, 'multiple_choice', 'Title Location', 'Where does title go?', {'question': 'Where does the <title> tag go?', 'options': ['Inside <head>', 'Inside <body>', 'After </html>', 'Inside <h1>'], 'correct_index': 0}),
            step(4, 'code_editor_challenge', 'Add a Title', 'Fix the page title.', {'prompt': 'Add a title to this page!', 'starter_code': '<!DOCTYPE html>\n<html>\n<head>\n</head>\n<body>\nLibrary of Info\n</body>\n</html>', 'language': 'html', 'validation': {'mode': 'contains', 'expected': '<title>'}}),
            step(5, 'story', 'Structure Restored', 'Grey world remains.', {'dialogue': [{'character': 'byte', 'text': 'Structure is restored!'}, {'character': 'pixel', 'text': 'Awesome… but it is still super grey.'}]}),
        ],
        'rewards': [('xp', 'Mission XP', 75, None), ('badge', 'Structure Builder', 0, 'structure-builder')],
    },
    {
        'id': 'add-color', 'title': 'Add Color', 'description': 'The world is drained of color! Help Pixel use CSS to bring back the vibrant colors.', 'character': 'pixel', 'difficulty': 'Beginner', 'xp': 75, 'coins': 15,
        'skills': ['CSS Basics', 'color Property'], 'language': 'html', 'num': 4, 'intro_arc': 'mission-4-intro', 'outro_arc': 'mission-4-outro',
        'steps': [
            step(1, 'story', 'Design Spark', 'Pixel notices the stolen spark.', {'dialogue': [{'character': 'pixel', 'text': 'No color means no sparkle. Let’s bring style back!'}]}),
            step(2, 'multiple_choice', 'What CSS Does', 'Choose the best answer.', {'question': 'CSS is used to…', 'options': ['Style and design web pages', 'Create the structure of pages', 'Make buttons clickable', 'Store data'], 'correct_index': 0}),
            step(3, 'true_false', 'CSS Color', 'True or false.', {'statement': 'CSS can change the color of text on a webpage.', 'correct_answer': True}),
            step(4, 'speech_bubble_fill', 'Color Property', 'Fill blank.', {'character': 'pixel', 'template': 'To change text color in CSS, use the ___ property.', 'answer': 'color', 'case_sensitive': False}),
            step(5, 'code_editor_challenge', 'Make it Pink', 'Use CSS to style heading.', {'prompt': 'Use CSS to make the heading pink! Use the color #E91E8C', 'starter_code': '<h1>Hello World!</h1>', 'language': 'html', 'validation': {'mode': 'contains_all', 'expected': ['color', '#E91E8C']}}),
            step(6, 'story', 'Color Returns', 'Celebration.', {'dialogue': [{'character': 'pixel', 'text': 'Color blooms across the world!'}, {'character': 'nova', 'text': 'That is amazing!'}]}),
        ],
        'rewards': [('xp', 'Mission XP', 75, None), ('badge', 'Color Artist', 0, 'color-artist')],
    },
    {
        'id': 'build-a-page', 'title': 'Build a Page', 'description': "Cyber Academy's homepage has vanished! Help Pixel build a new one with headings and paragraphs.", 'character': 'pixel', 'difficulty': 'Intermediate', 'xp': 100, 'coins': 20,
        'skills': ['HTML Headings', 'Paragraphs', '<p> Tag', 'Page Building'], 'language': 'html', 'num': 5, 'intro_arc': 'mission-5-intro', 'outro_arc': 'mission-5-outro',
        'steps': [
            step(1, 'story', 'Students Need Help', 'Homepage is gone.', {'dialogue': [{'character': 'pixel', 'text': 'Let’s rebuild the homepage so students can find class!'}]}),
            step(2, 'matching', 'Match Tags', 'Tag meaning matching.', {'prompt': 'Match each tag to what it does.', 'pairs': [{'left': '<h1>', 'right': 'Main heading'}, {'left': '<p>', 'right': 'Paragraph text'}, {'left': '<h2>', 'right': 'Subheading'}]}),
            step(3, 'multiple_choice', 'Heading Levels', 'Choose number.', {'question': 'How many heading levels does HTML have?', 'options': ['6 (h1 to h6)', '3 (h1 to h3)', '1 (just h1)', '10 (h1 to h10)'], 'correct_index': 0}),
            step(4, 'code_editor_challenge', 'Homepage Build', 'Add heading and paragraphs.', {'prompt': 'Build the Cyber Academy homepage! Add a heading and at least two paragraphs.', 'starter_code': '', 'language': 'html', 'validation': {'mode': 'contains_all', 'expected': ['<h1>', '<p>']}}),
            step(5, 'mini_project', 'Upgrade It', 'Add subheading and CSS.', {'prompt': 'Now add a subheading (<h2>) and style something with CSS!', 'starter_code': '<style>\n</style>\n<h1>Cyber Academy</h1>\n<p>Welcome!</p>', 'language': 'html', 'validation': {'mode': 'contains_all', 'expected': ['<h2>', 'style', 'color']}}),
            step(6, 'story', 'Flicker', 'Something breaks.', {'dialogue': [{'character': 'pixel', 'text': 'Page complete!'}, {'character': 'byte', 'text': 'Wait… did you see that glitch flicker?'}]}),
        ],
        'rewards': [('xp', 'Mission XP', 100, None), ('badge', 'Page Builder', 0, 'page-builder')],
    },
    {
        'id': 'meet-the-bug', 'title': 'Meet the Bug', 'description': "A Code Bug is chewing on the brackets! Help Byte fix the broken HTML before it's too late.", 'character': 'byte', 'difficulty': 'Intermediate', 'xp': 100, 'coins': 20,
        'skills': ['Debugging', 'Fixing Broken Tags'], 'language': 'html', 'num': 6, 'intro_arc': 'mission-6-intro', 'outro_arc': 'mission-6-outro', 'requires_arc': 'world-1-interlude',
        'steps': [
            step(1, 'story', 'Bug Attack', 'Dramatic entrance.', {'dialogue': [{'character': 'narrator', 'text': 'The Code Bug appears, chewing brackets and splattering digital slime!'}, {'character': 'byte', 'text': 'Stay calm. We debug one issue at a time.'}]}),
            step(2, 'multiple_choice', 'Debugging Meaning', 'Choose right answer.', {'question': 'What does “debugging” mean?', 'options': ['Finding and fixing errors in code', 'Adding bugs to code', 'Deleting all the code', 'Making the code longer'], 'correct_index': 0}),
            step(3, 'true_false', 'Closing Tags', 'True/false step.', {'statement': 'Every opening HTML tag needs a matching closing tag.', 'correct_answer': True}),
            step(4, 'debug_task', 'Fix Buggy Code 1', 'Repair broken tags.', {'prompt': 'The Code Bug chewed this code! Fix the broken tags.', 'buggy_code': '<h1>Welcome to the Internet\n<p>This is a great website</h1>', 'language': 'html', 'validation': {'mode': 'contains_all', 'expected': ['</h1>', '</p>']}}),
            step(5, 'debug_task', 'Fix Buggy Code 2', 'Repair again.', {'prompt': 'The Bug struck again! Fix this one too.', 'buggy_code': '<h2>About Us\n<p>We love coding!</h2>', 'language': 'html', 'validation': {'mode': 'contains', 'expected': '</p>'}}),
            step(6, 'story', 'Escaped', 'Bug flees.', {'dialogue': [{'character': 'byte', 'text': 'Got him— almost!'}, {'character': 'nova', 'text': 'It escaped to the Action Zone!'}]}),
        ],
        'rewards': [('xp', 'Mission XP', 100, None), ('badge', 'Bug Squasher', 0, 'bug-squasher')],
    },
    {
        'id': 'button-power', 'title': 'Button Power', 'description': 'The trap needs a trigger! Help Nova code a button to catch the Code Bugs.', 'character': 'nova', 'difficulty': 'Intermediate', 'xp': 100, 'coins': 20,
        'skills': ['HTML Buttons', '<button> Tag', 'Interactivity'], 'language': 'html', 'num': 7, 'intro_arc': 'mission-7-intro',
        'steps': [
            step(1, 'story', 'Trap Needs Trigger', 'Nova inspects trap.', {'dialogue': [{'character': 'nova', 'text': 'This trap is awesome, but it needs a trigger button!'}]}),
            step(2, 'multiple_choice', 'Button Tag', 'Choose tag.', {'question': 'Which HTML tag creates a clickable button?', 'options': ['<button>', '<input>', '<p>', '<h1>'], 'correct_index': 0}),
            step(3, 'speech_bubble_fill', 'Fill Button Tag', 'Complete sentence.', {'character': 'nova', 'template': 'To make a button, I use the ___ tag.', 'answer': 'button', 'case_sensitive': False}),
            step(4, 'code_editor_challenge', 'Create Button', 'Button text challenge.', {'prompt': "Create a button that says 'Catch the Bug!'", 'starter_code': '<h1>Bug Trap Control Panel</h1>', 'language': 'html', 'validation': {'mode': 'contains_all', 'expected': ['<button>', 'Catch the Bug!']}}),
            step(5, 'code_editor_challenge', 'Style Button', 'Add CSS styling.', {'prompt': 'Now add some style to make it look like a real trap button!', 'starter_code': '<style>\nbutton {\n}\n</style>\n<h1>Bug Trap</h1>\n<button>Catch the Bug!</button>', 'language': 'html', 'validation': {'mode': 'contains_all', 'expected': ['background', 'color']}}),
            step(6, 'story', 'Trap Armed', 'Net launches.', {'dialogue': [{'character': 'nova', 'text': 'Button works! Digital net launched!'}, {'character': 'byte', 'text': 'Next stop: the maze.'}]}),
        ],
        'rewards': [('xp', 'Mission XP', 100, None)],
    },
    {
        'id': 'robot-commands', 'title': 'Robot Commands', 'description': "Navigate Nova's Robot Companion through the maze using logic commands!", 'character': 'nova', 'difficulty': 'Intermediate', 'xp': 100, 'coins': 20,
        'skills': ['Logic', 'Sequences', 'Commands'], 'language': 'javascript', 'num': 8, 'intro_arc': 'mission-8-intro', 'outro_arc': 'mission-8-outro',
        'steps': [
            step(1, 'story', 'Maze Start', 'Obstacles everywhere.', {'dialogue': [{'character': 'nova', 'text': 'Robot Companion is ready, but the maze is packed with obstacles!'}]}),
            step(2, 'true_false', 'Order Matters', 'True/false.', {'statement': 'In coding, the order of commands matters.', 'correct_answer': True}),
            step(3, 'command_sequence', 'Maze Sequence 1', 'Order the commands.', {'prompt': 'Put the robot commands in the right order to reach the exit!', 'commands': ['moveForward()', 'turnRight()', 'moveForward()', 'moveForward()', 'turnLeft()', 'moveForward()'], 'correct_order': [0, 1, 2, 3, 4, 5]}),
            step(4, 'multiple_choice', 'Wrong Order Result', 'Choose outcome.', {'question': 'What happens if you put the commands in the wrong order?', 'options': ['The robot goes the wrong way', 'Nothing happens', 'The robot explodes', 'The commands fix themselves'], 'correct_index': 0}),
            step(5, 'command_sequence', 'Maze Sequence 2', 'Harder section.', {'prompt': 'The maze got harder! Navigate through this section.', 'commands': ['moveForward()', 'turnLeft()', 'moveForward()', 'turnRight()', 'moveForward()', 'turnRight()', 'moveForward()'], 'correct_order': [0, 1, 2, 3, 4, 5, 6]}),
            step(6, 'story', 'Exit Reached', 'Core path open.', {'dialogue': [{'character': 'nova', 'text': 'Path cleared!'}, {'character': 'byte', 'text': 'Time for the final stretch.'}]}),
        ],
        'rewards': [('xp', 'Mission XP', 100, None), ('badge', 'Logic Master', 0, 'logic-master')],
    },
    {
        'id': 'shero-website', 'title': 'SHERO Website', 'description': 'Build the SHEROs Headquarters page — a beacon of hope before the final battle!', 'character': 'pixel', 'difficulty': 'Advanced', 'xp': 150, 'coins': 30,
        'skills': ['Full Page Building', 'HTML + CSS Combined'], 'language': 'html', 'num': 9, 'intro_arc': 'mission-9-intro', 'outro_arc': 'mission-9-outro',
        'steps': [
            step(1, 'story', 'Beacon Plan', 'Build hope page.', {'dialogue': [{'character': 'pixel', 'text': 'Let’s create a page that says “I am a SHERO.”'}]}),
            step(2, 'multiple_choice', 'Complete Webpage', 'Choose correct statement.', {'question': 'A complete webpage needs…', 'options': ['Both HTML for structure and CSS for style', 'Only HTML', 'Only CSS', 'Only JavaScript'], 'correct_index': 0}),
            step(3, 'matching', 'Concept Matching', 'Match concept to language.', {'prompt': 'Match the concept to the language.', 'pairs': [{'left': 'Headings and paragraphs', 'right': 'HTML'}, {'left': 'Colors and fonts', 'right': 'CSS'}, {'left': 'Page structure', 'right': 'HTML'}, {'left': 'Background images', 'right': 'CSS'}]}),
            step(4, 'mini_project', 'Build SHERO HQ', 'Combine HTML and CSS.', {'prompt': "Build the SHERO HQ page! Include: a heading, a paragraph saying 'I am a SHERO', at least one styled element with CSS.", 'starter_code': '<style>\n</style>\n<body>\n</body>', 'language': 'html', 'validation': {'mode': 'contains_all', 'expected': ['<h1>', 'I am a SHERO', 'color']}}),
            step(5, 'story', 'Core Alert', 'Dr. Glitch spotted.', {'dialogue': [{'character': 'narrator', 'text': 'The page glows as a beacon.'}, {'character': 'byte', 'text': 'Dr. Glitch is at the Core! Team, assemble!'}]}),
        ],
        'rewards': [('xp', 'Mission XP', 150, None), ('badge', 'Web Designer', 0, 'web-designer')],
    },
    {
        'id': 'save-the-internet', 'title': 'Save the Internet', 'description': 'The final showdown! Work with all three SHEROs to defeat Dr. Glitch and restore the internet!', 'character': 'byte', 'difficulty': 'Advanced', 'xp': 200, 'coins': 50,
        'skills': ['HTML', 'CSS', 'Logic', 'Boss Battle'], 'language': 'html', 'num': 10, 'intro_arc': 'boss-battle-intro', 'outro_arc': 'boss-battle-victory',
        'steps': [
            step(1, 'story', 'Battle Mode', 'Boss intro.', {'dialogue': [{'character': 'narrator', 'text': 'SHERO Battle Mode: ACTIVATED! Three phases. Three heroes. One chance to save the internet.'}]}),
            step(2, 'boss_battle_phase', 'Phase 1', 'Rebuilding the Wall', {'phase': 1, 'title': 'Rebuilding the Wall'}),
            step(3, 'boss_battle_phase', 'Phase 2', 'Shield of Color', {'phase': 2, 'title': 'The Shield of Color'}),
            step(4, 'boss_battle_phase', 'Phase 3', 'Logic Trap', {'phase': 3, 'title': 'The Logic Trap'}),
            step(5, 'story', 'Victory', 'Final celebration.', {'dialogue': [{'character': 'narrator', 'text': 'Victory! Internet restored. You are officially a Code SHERO!'}]}),
        ],
        'rewards': [('xp', 'Mission XP', 200, None), ('badge', 'World 1 Champion', 0, 'world-1-champion')],
    },
]


class Command(BaseCommand):
    help = 'Seed World 1 missions, steps, and rewards'

    def handle(self, *args, **options):
        try:
            characters = {slug: Character.objects.get(slug=slug) for slug in ['byte', 'pixel', 'nova']}
        except Character.DoesNotExist:
            self.stdout.write(self.style.ERROR('Missing characters. Run seed_characters first.'))
            return

        missions = {}
        for mission_data in MISSION_DATA:
            intro_arc = StoryArc.objects.filter(id=mission_data.get('intro_arc')).first()
            outro_arc = StoryArc.objects.filter(id=mission_data.get('outro_arc')).first()
            requires_arc = StoryArc.objects.filter(id=mission_data.get('requires_arc')).first()

            mission, _ = Mission.objects.update_or_create(
                id=mission_data['id'],
                defaults={
                    'num': mission_data['num'],
                    'title': mission_data['title'],
                    'description': mission_data['description'],
                    'long_description': mission_data['description'],
                    'character': characters[mission_data['character']],
                    'difficulty': mission_data['difficulty'],
                    'xp': mission_data['xp'],
                    'coins': mission_data['coins'],
                    'skills': mission_data['skills'],
                    'mentor_tip': 'Take it one step at a time, SHERO.',
                    'why_learn_this': 'Coding helps you build, solve problems, and create positive change.',
                    'estimated_minutes': 12,
                    'starter_code': '',
                    'language': mission_data['language'],
                    'unlock_after': missions.get(MISSION_DATA[mission_data['num'] - 2]['id']) if mission_data['num'] > 1 else None,
                    'intro_arc': intro_arc,
                    'outro_arc': outro_arc,
                    'requires_arc': requires_arc,
                    'is_active': True,
                },
            )
            missions[mission.id] = mission

            for s in mission_data['steps']:
                MissionStep.objects.update_or_create(
                    mission=mission,
                    num=s['num'],
                    defaults={
                        'step_type': s['step_type'],
                        'title': s['title'],
                        'description': s['description'],
                        'hint': s['hint'],
                        'content': s['content'],
                        'validation_type': '',
                        'validation_value': '',
                    },
                )
            MissionStep.objects.filter(mission=mission).exclude(num__in=[s['num'] for s in mission_data['steps']]).delete()

            MissionReward.objects.filter(mission=mission).delete()
            for reward_type, label, value, badge_slug in mission_data['rewards']:
                badge = Badge.objects.filter(id=badge_slug).first() if badge_slug else None
                MissionReward.objects.update_or_create(
                    mission=mission,
                    type=reward_type,
                    label=label,
                    defaults={'value': value, 'badge': badge},
                )

        self.stdout.write(self.style.SUCCESS(f'Seeded {len(MISSION_DATA)} World 1 missions.'))
