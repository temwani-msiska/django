from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from accounts.models import ChildPreferences, ChildProfile, ParentUser


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

        self.stdout.write(self.style.SUCCESS('Demo data seeded'))
