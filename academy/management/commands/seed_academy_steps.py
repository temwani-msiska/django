"""
Seeds lesson steps for the first 3 lessons of HTML Basics and CSS Styling.
This gives the pilot enough academy content to demonstrate the learning flow.
"""

from django.core.management.base import BaseCommand

from academy.models import Lesson, LessonStep


class Command(BaseCommand):
    help = 'Seed academy lesson steps for pilot content'

    def handle(self, *args, **options):
        self.seed_html_lesson_1()
        self.seed_html_lesson_2()
        self.seed_html_lesson_3()
        self.seed_css_lesson_1()
        self.seed_css_lesson_2()
        self.seed_css_lesson_3()
        self.stdout.write(self.style.SUCCESS('✓ Academy lesson steps seeded'))

    def _seed_steps(self, lesson, steps):
        for step_data in steps:
            LessonStep.objects.update_or_create(
                lesson=lesson,
                number=step_data['number'],
                defaults=step_data,
            )
        self.stdout.write(f'  ✓ {lesson.title}: {len(steps)} steps')

    def seed_html_lesson_1(self):
        lesson = Lesson.objects.filter(track__id='track-html', order=1).first()
        if not lesson:
            self.stdout.write('  ⚠ HTML Basics lesson 1 not found, skipping')
            return
        steps = [
            {
                'number': 1,
                'step_type': 'explanation',
                'title': 'What is HTML?',
                'content': {
                    'text': (
                        "HTML stands for HyperText Markup Language. It's the language that builds "
                        "every website you see! HTML uses special tags to tell the browser what to "
                        "show — headings, paragraphs, images, and more."
                    ),
                },
                'hint': '',
                'is_required': True,
            },
            {
                'number': 2,
                'step_type': 'example',
                'title': 'Your First Tag',
                'content': {
                    'text': 'This is a heading tag. It makes text big and bold! Every tag has an opening part and a closing part.',
                    'code': '<h1>Hello, World!</h1>',
                    'language': 'html',
                },
                'hint': '',
                'is_required': True,
            },
            {
                'number': 3,
                'step_type': 'multiple_choice',
                'title': 'Tag Check',
                'content': {
                    'question': 'What does HTML stand for?',
                    'options': [
                        'HyperText Markup Language',
                        'High Tech Modern Language',
                        'Home Tool Making Language',
                        'Helpful Text Making Lessons',
                    ],
                    'correct_index': 0,
                },
                'hint': 'It has the words "Markup" and "Language" in it!',
                'is_required': True,
            },
            {
                'number': 4,
                'step_type': 'true_false',
                'title': 'True or False?',
                'content': {
                    'statement': 'Every HTML tag needs an opening tag and a closing tag.',
                    'correct_answer': True,
                },
                'hint': 'Think about <h1> and </h1>',
                'is_required': True,
            },
            {
                'number': 5,
                'step_type': 'guided_coding',
                'title': 'Write Your First Tag',
                'content': {
                    'prompt': 'Type a heading tag that says "Hello!" — use the h1 tag.',
                    'starter_code': '<!-- Type your heading below -->\n',
                    'language': 'html',
                    'validation': {'mode': 'contains_all', 'expected': ['<h1>', '</h1>']},
                },
                'hint': 'A heading looks like <h1>Your text here</h1>',
                'is_required': True,
            },
            {
                'number': 6,
                'step_type': 'fill_in',
                'title': 'Fill in the Blank',
                'content': {
                    'template': 'The ___ tag creates the biggest heading on a page.',
                    'answer': 'h1',
                    'case_sensitive': False,
                },
                'hint': "It's the tag we just used!",
                'is_required': True,
            },
            {
                'number': 7,
                'step_type': 'guided_coding',
                'title': 'Add a Paragraph',
                'content': {
                    'prompt': 'Now add a paragraph below your heading. Use the <p> tag to write a sentence about yourself!',
                    'starter_code': '<h1>Hello!</h1>\n<!-- Add a paragraph below -->\n',
                    'language': 'html',
                    'validation': {'mode': 'contains_all', 'expected': ['<p>', '</p>']},
                },
                'hint': 'A paragraph looks like <p>Your sentence here</p>',
                'is_required': True,
            },
            {
                'number': 8,
                'step_type': 'reflection',
                'title': 'What Did You Learn?',
                'content': {
                    'question': 'What was the most interesting thing you learned about HTML?',
                    'type': 'free_text',
                },
                'hint': '',
                'is_required': False,
            },
        ]
        self._seed_steps(lesson, steps)

    def seed_html_lesson_2(self):
        lesson = Lesson.objects.filter(track__id='track-html', order=2).first()
        if not lesson:
            self.stdout.write('  ⚠ HTML Basics lesson 2 not found, skipping')
            return
        steps = [
            {
                'number': 1,
                'step_type': 'explanation',
                'title': 'Heading Levels',
                'content': {
                    'text': (
                        'HTML has 6 heading levels — from <h1> (the biggest) to <h6> (the smallest). '
                        'Think of them like a book: h1 is the book title, h2 is a chapter title, '
                        'and h3 is a section title.'
                    ),
                },
                'hint': '',
                'is_required': True,
            },
            {
                'number': 2,
                'step_type': 'example',
                'title': 'All the Headings',
                'content': {
                    'text': 'Here are all 6 heading levels. Notice how each one gets smaller!',
                    'code': (
                        '<h1>I am h1 — the biggest!</h1>\n'
                        '<h2>I am h2</h2>\n<h3>I am h3</h3>\n'
                        '<h4>I am h4</h4>\n<h5>I am h5</h5>\n'
                        '<h6>I am h6 — the smallest</h6>'
                    ),
                    'language': 'html',
                },
                'hint': '',
                'is_required': True,
            },
            {
                'number': 3,
                'step_type': 'multiple_choice',
                'title': 'Which is Biggest?',
                'content': {
                    'question': 'Which heading tag creates the LARGEST text?',
                    'options': ['<h1>', '<h6>', '<h3>', '<heading>'],
                    'correct_index': 0,
                },
                'hint': 'The smaller the number, the bigger the heading!',
                'is_required': True,
            },
            {
                'number': 4,
                'step_type': 'guided_coding',
                'title': 'Build a Page Structure',
                'content': {
                    'prompt': 'Create a page with an h1 title, an h2 subtitle, and a paragraph. Make it about your favourite hobby!',
                    'starter_code': '<!-- Build your page here -->\n',
                    'language': 'html',
                    'validation': {'mode': 'contains_all', 'expected': ['<h1>', '<h2>', '<p>']},
                },
                'hint': 'Use <h1> for the main title, <h2> for a subtitle, and <p> for a paragraph.',
                'is_required': True,
            },
            {
                'number': 5,
                'step_type': 'true_false',
                'title': 'Heading Facts',
                'content': {
                    'statement': '<h6> creates bigger text than <h1>.',
                    'correct_answer': False,
                },
                'hint': 'Remember: smaller number = bigger heading!',
                'is_required': True,
            },
            {
                'number': 6,
                'step_type': 'guided_coding',
                'title': 'Mini Challenge',
                'content': {
                    'prompt': (
                        'Build a page about Code SHEROs! Use h1 for the title "Code SHEROs", '
                        'h2 for "Our Mission", and a paragraph explaining what SHEROs do.'
                    ),
                    'starter_code': '<!-- Code SHEROs page -->\n',
                    'language': 'html',
                    'validation': {'mode': 'contains_all', 'expected': ['<h1>', 'SHERO', '<h2>', '<p>']},
                },
                'hint': 'Start with <h1>Code SHEROs</h1> then add your h2 and paragraph below.',
                'is_required': True,
            },
        ]
        self._seed_steps(lesson, steps)

    def seed_html_lesson_3(self):
        lesson = Lesson.objects.filter(track__id='track-html', order=3).first()
        if not lesson:
            self.stdout.write('  ⚠ HTML Basics lesson 3 not found, skipping')
            return
        steps = [
            {
                'number': 1,
                'step_type': 'explanation',
                'title': 'Connecting Pages',
                'content': {
                    'text': (
                        "Links are what make the web a WEB! They connect one page to another. "
                        "The <a> tag (anchor tag) creates a clickable link. You tell it WHERE to go "
                        "using the href attribute."
                    ),
                },
                'hint': '',
                'is_required': True,
            },
            {
                'number': 2,
                'step_type': 'example',
                'title': 'Your First Link',
                'content': {
                    'text': "Here's a link that goes to a website. The text between the tags is what people click on.",
                    'code': '<a href="https://codesheros.co.zm">Visit Code SHEROs!</a>',
                    'language': 'html',
                },
                'hint': '',
                'is_required': True,
            },
            {
                'number': 3,
                'step_type': 'fill_in',
                'title': 'Tag Name',
                'content': {
                    'template': 'The ___ tag creates a clickable link.',
                    'answer': 'a',
                    'case_sensitive': False,
                },
                'hint': 'It stands for "anchor"!',
                'is_required': True,
            },
            {
                'number': 4,
                'step_type': 'multiple_choice',
                'title': 'Link Attribute',
                'content': {
                    'question': 'Which attribute tells a link WHERE to go?',
                    'options': ['href', 'src', 'link', 'goto'],
                    'correct_index': 0,
                },
                'hint': 'It starts with "h" and stands for "hypertext reference"!',
                'is_required': True,
            },
            {
                'number': 5,
                'step_type': 'guided_coding',
                'title': 'Make a Link',
                'content': {
                    'prompt': 'Create a link that says "Learn to Code" and points to https://codesheros.co.zm',
                    'starter_code': '<!-- Create your link here -->\n',
                    'language': 'html',
                    'validation': {'mode': 'contains_all', 'expected': ['<a', 'href', '</a>']},
                },
                'hint': 'Use <a href="URL">Link text</a>',
                'is_required': True,
            },
            {
                'number': 6,
                'step_type': 'guided_coding',
                'title': 'Page with Links',
                'content': {
                    'prompt': 'Build a page with a heading, a paragraph, and at least one link!',
                    'starter_code': '<!-- Build a complete page with links -->\n',
                    'language': 'html',
                    'validation': {'mode': 'contains_all', 'expected': ['<h1>', '<p>', '<a', 'href']},
                },
                'hint': "Combine what you've learned: h1 for title, p for text, a for links!",
                'is_required': True,
            },
        ]
        self._seed_steps(lesson, steps)

    def seed_css_lesson_1(self):
        lesson = Lesson.objects.filter(track__id='track-css', order=1).first()
        if not lesson:
            self.stdout.write('  ⚠ CSS Styling lesson 1 not found, skipping')
            return
        steps = [
            {
                'number': 1,
                'step_type': 'explanation',
                'title': 'What is CSS?',
                'content': {
                    'text': (
                        "CSS stands for Cascading Style Sheets. If HTML is the skeleton of a website "
                        "(the structure), CSS is the clothes and makeup (the style)! CSS lets you "
                        "change colors, fonts, sizes, spacing, and so much more."
                    ),
                },
                'hint': '',
                'is_required': True,
            },
            {
                'number': 2,
                'step_type': 'example',
                'title': 'CSS in Action',
                'content': {
                    'text': "Here's HTML without CSS (plain) vs with CSS (styled). The <style> tag is where CSS lives!",
                    'code': (
                        '<style>\n  h1 {\n    color: #E91E8C;\n    font-size: 36px;\n  }\n'
                        '  p {\n    color: #333;\n  }\n</style>\n\n'
                        '<h1>Styled Heading!</h1>\n<p>This text has a custom color.</p>'
                    ),
                    'language': 'html',
                },
                'hint': '',
                'is_required': True,
            },
            {
                'number': 3,
                'step_type': 'true_false',
                'title': 'CSS Fact',
                'content': {
                    'statement': 'CSS is used to style and design web pages.',
                    'correct_answer': True,
                },
                'hint': 'Think about colors, fonts, and layout!',
                'is_required': True,
            },
            {
                'number': 4,
                'step_type': 'multiple_choice',
                'title': 'CSS Purpose',
                'content': {
                    'question': 'What does CSS change about a webpage?',
                    'options': [
                        'Colors, fonts, and layout',
                        'The text content',
                        'The web address',
                        'The internet speed',
                    ],
                    'correct_index': 0,
                },
                'hint': 'CSS is all about how things LOOK!',
                'is_required': True,
            },
            {
                'number': 5,
                'step_type': 'fill_in',
                'title': 'Fill in the Blank',
                'content': {
                    'template': 'CSS stands for Cascading ___ Sheets.',
                    'answer': 'Style',
                    'case_sensitive': False,
                },
                'hint': 'CSS makes websites look ___ish!',
                'is_required': True,
            },
            {
                'number': 6,
                'step_type': 'guided_coding',
                'title': 'Your First Style',
                'content': {
                    'prompt': 'Make the heading pink! Add a color property inside the h1 CSS rule. Use the color #E91E8C.',
                    'starter_code': '<style>\n  h1 {\n    /* Add color here */\n    \n  }\n</style>\n\n<h1>Hello, Style!</h1>',
                    'language': 'html',
                    'validation': {'mode': 'contains_all', 'expected': ['color', '#E91E8C']},
                },
                'hint': 'Inside the h1 curly braces, type: color: #E91E8C;',
                'is_required': True,
            },
        ]
        self._seed_steps(lesson, steps)

    def seed_css_lesson_2(self):
        lesson = Lesson.objects.filter(track__id='track-css', order=2).first()
        if not lesson:
            self.stdout.write('  ⚠ CSS Styling lesson 2 not found, skipping')
            return
        steps = [
            {
                'number': 1,
                'step_type': 'explanation',
                'title': 'Color Everywhere!',
                'content': {
                    'text': (
                        'CSS has two main color properties: "color" changes TEXT color, and '
                        '"background-color" changes the BACKGROUND color. You can use color names '
                        '(red, blue, pink) or hex codes (#FF0000, #0000FF).'
                    ),
                },
                'hint': '',
                'is_required': True,
            },
            {
                'number': 2,
                'step_type': 'example',
                'title': 'Text vs Background',
                'content': {
                    'text': 'See the difference between color and background-color!',
                    'code': (
                        '<style>\n  .text-demo { color: blue; }\n'
                        '  .bg-demo { background-color: yellow; }\n'
                        '  .both { color: white; background-color: purple; }\n</style>\n\n'
                        '<p class="text-demo">Blue text</p>\n'
                        '<p class="bg-demo">Yellow background</p>\n'
                        '<p class="both">White text on purple!</p>'
                    ),
                    'language': 'html',
                },
                'hint': '',
                'is_required': True,
            },
            {
                'number': 3,
                'step_type': 'multiple_choice',
                'title': 'Which Property?',
                'content': {
                    'question': 'Which CSS property changes the BACKGROUND color?',
                    'options': ['background-color', 'color', 'bg-color', 'fill'],
                    'correct_index': 0,
                },
                'hint': 'It literally has "background" in the name!',
                'is_required': True,
            },
            {
                'number': 4,
                'step_type': 'guided_coding',
                'title': 'Color a Card',
                'content': {
                    'prompt': 'Style the card: make the background purple (#7B2D8E) and the text white!',
                    'starter_code': (
                        '<style>\n  .card {\n    padding: 20px;\n'
                        '    /* Add background-color and color here */\n    \n  }\n</style>\n\n'
                        '<div class="card">\n  <h2>SHERO Card</h2>\n  <p>I am a Code SHERO!</p>\n</div>'
                    ),
                    'language': 'html',
                    'validation': {
                        'mode': 'contains_all',
                        'expected': ['background-color', '#7B2D8E', 'color', 'white'],
                    },
                },
                'hint': 'Add two lines: background-color: #7B2D8E; and color: white;',
                'is_required': True,
            },
            {
                'number': 5,
                'step_type': 'guided_coding',
                'title': 'Rainbow Page',
                'content': {
                    'prompt': 'Create a colorful page! Make the body background light pink and add at least 2 colored headings.',
                    'starter_code': (
                        '<style>\n  body {\n    /* Add background-color */\n  }\n'
                        '  /* Add styles for your headings */\n</style>\n\n'
                        '<h1>My Colorful Page</h1>\n<h2>So many colors!</h2>\n'
                        '<p>CSS makes everything beautiful.</p>'
                    ),
                    'language': 'html',
                    'validation': {'mode': 'contains_all', 'expected': ['background-color', 'color']},
                },
                'hint': 'Try: body { background-color: pink; } and h1 { color: purple; }',
                'is_required': True,
            },
        ]
        self._seed_steps(lesson, steps)

    def seed_css_lesson_3(self):
        lesson = Lesson.objects.filter(track__id='track-css', order=3).first()
        if not lesson:
            self.stdout.write('  ⚠ CSS Styling lesson 3 not found, skipping')
            return
        steps = [
            {
                'number': 1,
                'step_type': 'explanation',
                'title': 'Font Power!',
                'content': {
                    'text': (
                        'CSS lets you change how text looks with properties like font-size (how big), '
                        'font-family (which font), font-weight (bold or normal), and text-align '
                        '(left, center, right). These are like the controls on a text editor!'
                    ),
                },
                'hint': '',
                'is_required': True,
            },
            {
                'number': 2,
                'step_type': 'example',
                'title': 'Font Properties',
                'content': {
                    'text': 'Here are the main font properties in action!',
                    'code': (
                        '<style>\n  h1 {\n    font-size: 48px;\n'
                        '    font-family: Arial, sans-serif;\n    text-align: center;\n  }\n'
                        '  p {\n    font-size: 18px;\n    font-weight: bold;\n  }\n</style>\n\n'
                        '<h1>Big Centered Title</h1>\n<p>Bold paragraph text</p>'
                    ),
                    'language': 'html',
                },
                'hint': '',
                'is_required': True,
            },
            {
                'number': 3,
                'step_type': 'fill_in',
                'title': 'Font Size',
                'content': {
                    'template': 'The CSS property ___ changes how big text is.',
                    'answer': 'font-size',
                    'case_sensitive': False,
                },
                'hint': "It's font-????",
                'is_required': True,
            },
            {
                'number': 4,
                'step_type': 'multiple_choice',
                'title': 'Center Text',
                'content': {
                    'question': 'Which property centers text horizontally?',
                    'options': [
                        'text-align: center',
                        'text-center: true',
                        'align: middle',
                        'center-text: yes',
                    ],
                    'correct_index': 0,
                },
                'hint': 'Think: text-?????',
                'is_required': True,
            },
            {
                'number': 5,
                'step_type': 'guided_coding',
                'title': 'Style a SHERO Badge',
                'content': {
                    'prompt': 'Create a centered heading with font-size 48px and a paragraph with font-size 20px. Make it look like a SHERO badge!',
                    'starter_code': '<style>\n  /* Style your badge */\n</style>\n\n<h1>⭐ Code SHERO ⭐</h1>\n<p>Official SHERO Badge</p>',
                    'language': 'html',
                    'validation': {'mode': 'contains_all', 'expected': ['font-size', 'text-align']},
                },
                'hint': 'Use font-size for the size and text-align: center to center everything!',
                'is_required': True,
            },
        ]
        self._seed_steps(lesson, steps)
