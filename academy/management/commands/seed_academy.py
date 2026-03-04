from django.core.management.base import BaseCommand

from academy.models import LearningTrack, Lesson


class Command(BaseCommand):
    help = 'Seed academy tracks and lessons'

    def handle(self, *args, **options):
        track, _ = LearningTrack.objects.update_or_create(
            id='track-html',
            defaults={'title': 'HTML Basics', 'description': 'Build your first web pages', 'icon': '🌐', 'color': '#FF7675', 'order': 1},
        )
        Lesson.objects.update_or_create(
            id='html-1',
            defaults={'track': track, 'title': 'Intro to HTML', 'description': 'Learn tags and structure.', 'duration': '10 min', 'order': 1},
        )
        self.stdout.write(self.style.SUCCESS('Academy seeded'))
