from django.core.management.base import BaseCommand

from academy.models import LearningTrack, Lesson


# (id, title, description, icon, color, order)
TRACKS = [
    (
        'track-logic',
        'Logic & Problem Solving',
        'Build computational thinking before and during coding.',
        '🧩', '#00B894', 1,
    ),
    (
        'track-html',
        'HTML Basics',
        'Help kids understand the structure of a webpage.',
        '🌐', '#FF7675', 2,
    ),
    (
        'track-css',
        'CSS Styling',
        'Teach kids how to make webpages colourful and beautiful.',
        '🎨', '#6C5CE7', 3,
    ),
    (
        'track-js',
        'JavaScript Intro',
        'Introduce interactivity and logic using simple JavaScript.',
        '⚙️', '#0984E3', 4,
    ),
    (
        'track-projects',
        'Web Projects Studio',
        'Combine HTML, CSS, and JavaScript into real mini-projects.',
        '🚀', '#E17055', 5,
    ),
    (
        'track-safety',
        'Internet Safety & Digital Skills',
        'Teach kids to be smart and safe online.',
        '🛡️', '#FDCB6E', 6,
    ),
    (
        'track-games',
        'Game Logic Basics',
        'Make coding exciting through simple game thinking.',
        '🎮', '#E84393', 7,
    ),
    (
        'track-design',
        'Creative Design for Coders',
        'Teach visual creativity alongside coding.',
        '✏️', '#00CEC9', 8,
    ),
]

# (lesson_id, title, description, duration)
LESSONS = {
    'track-logic': [
        ('logic-1', 'Think Step by Step', 'Break a problem into smaller pieces.', '8 min'),
        ('logic-2', 'Patterns & Sequences', 'Find patterns and predict what comes next.', '9 min'),
        ('logic-3', 'Debugging 101', 'Spot mistakes and fix them.', '10 min'),
        ('logic-4', 'Algorithms', 'Write simple step-by-step instructions.', '10 min'),
        ('logic-5', 'Logic Challenge', 'Complete puzzle-based coding missions.', '12 min'),
    ],
    'track-html': [
        ('html-1', 'Your First Webpage', 'Learn what HTML is and create a page with a heading and paragraph.', '8 min'),
        ('html-2', 'Tags & Elements', 'Understand opening tags, closing tags, and how elements work together.', '9 min'),
        ('html-3', 'Lists & Links', 'Make bullet lists, numbered lists, and clickable links.', '10 min'),
        ('html-4', 'Images & Media', 'Add pictures, audio, and video to a webpage.', '10 min'),
        ('html-5', 'Forms & Input', 'Create forms with text boxes, buttons, and checkboxes.', '11 min'),
        ('html-6', 'HTML Project', 'Build a full webpage about a favourite Zambian animal, hero, or place.', '15 min'),
    ],
    'track-css': [
        ('css-1', 'Colours & Backgrounds', 'Change text colours and add background colours.', '8 min'),
        ('css-2', 'Fonts & Text', 'Style text with font size, weight, and alignment.', '9 min'),
        ('css-3', 'Box Model', 'Learn padding, borders, and margins.', '10 min'),
        ('css-4', 'Flexbox Layout', 'Arrange items neatly on the page.', '11 min'),
        ('css-5', 'Responsive Design', 'Make webpages look nice on phones, tablets, and laptops.', '11 min'),
        ('css-6', 'CSS Project', 'Style a tourism or school event page using everything learned.', '15 min'),
    ],
    'track-js': [
        ('js-1', 'Hello JavaScript', 'Write the first JavaScript code and see it work.', '8 min'),
        ('js-2', 'Variables & Data', 'Store names, numbers, and other values.', '9 min'),
        ('js-3', 'If/Else Decisions', 'Make programs choose different actions.', '10 min'),
        ('js-4', 'Loops & Repetition', 'Repeat tasks using loops.', '10 min'),
        ('js-5', 'Functions', 'Group code into reusable actions.', '11 min'),
        ('js-6', 'JavaScript Project', 'Build an interactive quiz or simple score tracker.', '15 min'),
    ],
    'track-projects': [
        ('projects-1', 'My Profile Page', 'Create a personal profile page with HTML, CSS, and JavaScript.', '12 min'),
        ('projects-2', 'My Dream School Website', 'Design and build a website for your dream school.', '14 min'),
        ('projects-3', 'Zambia Fact Page', 'Build an informative page about Zambia with images and links.', '14 min'),
        ('projects-4', 'Interactive Quiz Page', 'Create a fun quiz page with scoring using JavaScript.', '15 min'),
        ('projects-5', 'Final Showcase Project', 'Combine everything into a final showcase project.', '18 min'),
    ],
    'track-safety': [
        ('safety-1', 'What is the Internet?', 'Discover how the internet works and connects people.', '8 min'),
        ('safety-2', 'Passwords & Privacy', 'Learn to create strong passwords and protect personal info.', '9 min'),
        ('safety-3', 'Spotting Scams', 'Identify fake messages, links, and online tricks.', '9 min'),
        ('safety-4', 'Being Kind Online', 'Practice digital kindness and responsible communication.', '8 min'),
        ('safety-5', 'Digital Hero Challenge', 'Complete a challenge proving you are a smart digital citizen.', '10 min'),
    ],
    'track-games': [
        ('games-1', 'What Makes a Game?', 'Explore the basic parts that make up a game.', '8 min'),
        ('games-2', 'Scores & Points', 'Learn how scoring systems work in games.', '9 min'),
        ('games-3', 'Player Choices', 'Add decision-making for the player.', '10 min'),
        ('games-4', 'Win and Lose Rules', 'Create rules that decide when a player wins or loses.', '10 min'),
        ('games-5', 'Build a Mini Game Idea', 'Design and plan your own mini game from scratch.', '12 min'),
    ],
    'track-design': [
        ('design-1', 'Choosing Colours', 'Pick colour palettes that look great together.', '8 min'),
        ('design-2', 'Designing Buttons & Cards', 'Create attractive buttons and card components.', '9 min'),
        ('design-3', 'Page Layout Basics', 'Understand layout principles for clean page design.', '10 min'),
        ('design-4', 'Icons, Images, and Style', 'Use icons and images to enhance visual appeal.', '10 min'),
        ('design-5', 'Design a SHERO Dashboard', 'Design a full dashboard for your SHERO profile.', '14 min'),
    ],
}


class Command(BaseCommand):
    help = 'Seed academy tracks and lessons (8 tracks / 44 lessons)'

    def handle(self, *args, **options):
        total_lessons = 0

        for track_id, title, description, icon, color, order in TRACKS:
            track, _ = LearningTrack.objects.update_or_create(
                id=track_id,
                defaults={
                    'title': title,
                    'description': description,
                    'icon': icon,
                    'color': color,
                    'order': order,
                },
            )

            previous = None
            for num, (lesson_id, lesson_title, lesson_desc, duration) in enumerate(LESSONS[track_id], start=1):
                lesson, _ = Lesson.objects.update_or_create(
                    id=lesson_id,
                    defaults={
                        'track': track,
                        'title': lesson_title,
                        'description': lesson_desc,
                        'duration': duration,
                        'order': num,
                        'unlock_after': previous,
                    },
                )
                previous = lesson
                total_lessons += 1

        self.stdout.write(self.style.SUCCESS(
            f'Academy seeded (tracks={len(TRACKS)}, lessons={total_lessons})'
        ))
