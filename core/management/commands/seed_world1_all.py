from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed all World 1 content (story, badges, missions, boss battle)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding World 1 content...\n')

        self.stdout.write('  1. Story arcs and scenes...')
        call_command('seed_world1_story')
        self.stdout.write(self.style.SUCCESS(' ✓'))

        self.stdout.write('  2. World 1 badges...')
        call_command('seed_world1_badges')
        self.stdout.write(self.style.SUCCESS(' ✓'))

        self.stdout.write('  3. Missions and steps...')
        call_command('seed_world1_missions')
        self.stdout.write(self.style.SUCCESS(' ✓'))

        self.stdout.write('  4. Boss battle...')
        call_command('seed_world1_boss')
        self.stdout.write(self.style.SUCCESS(' ✓'))

        self.stdout.write(self.style.SUCCESS('\n🎉 World 1 fully seeded!'))

        from missions.models import BossBattle, Mission, MissionStep
        from rewards.models import Badge
        from story.models import Scene, StoryArc

        world1_arc_count = (
            StoryArc.objects.filter(id__startswith='world-1').count()
            + StoryArc.objects.filter(id__startswith='mission-').count()
            + StoryArc.objects.filter(id__startswith='boss-').count()
        )

        self.stdout.write(f'  Story Arcs: {world1_arc_count}')
        self.stdout.write(f'  Scenes: {Scene.objects.count()}')
        self.stdout.write(f'  Missions: {Mission.objects.count()}')
        self.stdout.write(f'  Mission Steps: {MissionStep.objects.count()}')
        self.stdout.write(f'  Boss Battles: {BossBattle.objects.count()}')
        self.stdout.write(f'  Badges: {Badge.objects.count()}')
