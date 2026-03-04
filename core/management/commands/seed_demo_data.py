from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from accounts.models import ChildPreferences, ChildProfile, ParentUser
from missions.models import Mission, MissionProgress
from rewards.models import Badge, EarnedBadge


class Command(BaseCommand):
    help = 'Seed Zambian demo data'

    def handle(self, *args, **options):
        parent, _ = ParentUser.objects.update_or_create(
            email='grace.mwale@email.co.zm',
            defaults={'name': 'Mrs. Mwale', 'username': 'grace.mwale@email.co.zm'},
        )
        parent.set_password('Password123!')
        parent.save()

        chanda, _ = ChildProfile.objects.update_or_create(
            parent=parent,
            nickname='Chanda',
            defaults={'pin': make_password('1234'), 'avatar_character': 'byte', 'level': 3, 'xp': 350},
        )
        mutale, _ = ChildProfile.objects.update_or_create(
            parent=parent,
            nickname='Mutale',
            defaults={'pin': make_password('5678'), 'avatar_character': 'pixel', 'level': 2, 'xp': 180},
        )

        ChildPreferences.objects.get_or_create(child=chanda)
        ChildPreferences.objects.get_or_create(child=mutale)

        for child, completed_ids in ((chanda, ['byte-1', 'byte-2']), (mutale, ['pixel-1'])):
            for mission in Mission.objects.filter(id__in=completed_ids):
                MissionProgress.objects.update_or_create(
                    child=child,
                    mission=mission,
                    defaults={'status': 'completed', 'progress': 100},
                )

        for badge in Badge.objects.all()[:3]:
            EarnedBadge.objects.get_or_create(child=chanda, badge=badge)
        first_badge = Badge.objects.first()
        if first_badge:
            EarnedBadge.objects.get_or_create(child=mutale, badge=first_badge)

        self.stdout.write(self.style.SUCCESS('Demo data seeded (Mrs. Mwale, Chanda, Mutale)'))
