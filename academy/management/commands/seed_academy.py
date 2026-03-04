from django.core.management.base import BaseCommand

from academy.models import LearningTrack, Lesson


TRACKS = [
    ('track-html', 'HTML Fundamentals', 'Structure web pages', '🌐', '#FF7675', 1, 6),
    ('track-css', 'CSS Styling', 'Style and layout pages', '🎨', '#6C5CE7', 2, 6),
    ('track-js', 'JavaScript Basics', 'Add interactivity with JS', '⚙️', '#0984E3', 3, 6),
    ('track-logic', 'Logic & Problem Solving', 'Think like a coder', '🧩', '#00B894', 4, 5),
]


class Command(BaseCommand):
    help = 'Seed academy tracks and lessons (4 tracks / 23 lessons)'

    def handle(self, *args, **options):
        total_lessons = 0
        for track_id, title, description, icon, color, order, lesson_count in TRACKS:
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
            prefix = track_id.replace('track-', '')
            for num in range(1, lesson_count + 1):
                lesson, _ = Lesson.objects.update_or_create(
                    id=f'{prefix}-{num}',
                    defaults={
                        'track': track,
                        'title': f'{title} Lesson {num}',
                        'description': f'Learn {title.lower()} concept {num}.',
                        'duration': f'{8 + num} min',
                        'order': num,
                        'unlock_after': previous,
                    },
                )
                previous = lesson
                total_lessons += 1

        self.stdout.write(self.style.SUCCESS(f'Academy seeded (tracks={len(TRACKS)}, lessons={total_lessons})'))
