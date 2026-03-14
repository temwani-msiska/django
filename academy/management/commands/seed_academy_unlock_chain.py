from django.core.management.base import BaseCommand

from academy.models import LearningTrack, Lesson


class Command(BaseCommand):
    help = 'Set unlock_after chain on all academy lessons within each track'

    def handle(self, *args, **options):
        tracks = LearningTrack.objects.all().order_by('order')

        for track in tracks:
            lessons = list(track.lessons.order_by('order'))

            if len(lessons) == 0:
                continue

            # First lesson: no prerequisite (always available)
            first = lessons[0]
            first.unlock_after = None
            first.save()
            self.stdout.write(f'  {track.title}: {first.title} → always available')

            # Each subsequent lesson requires the previous
            for i in range(1, len(lessons)):
                lessons[i].unlock_after = lessons[i - 1]
                lessons[i].save()
                self.stdout.write(
                    f'  {track.title}: {lessons[i].title} → requires {lessons[i - 1].title}'
                )

        self.stdout.write(self.style.SUCCESS('✓ Lesson unlock chains set'))
