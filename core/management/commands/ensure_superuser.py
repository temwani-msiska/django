import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create/update a superuser from environment variables if provided.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '').strip().lower()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stdout.write(self.style.WARNING('Skipping superuser creation. Set DJANGO_SUPERUSER_PASSWORD.'))
            return

        # If username looks like an email and explicit email missing, use it.
        if not email and '@' in username:
            email = username.lower()

        if not email:
            self.stdout.write(self.style.WARNING('Skipping superuser creation. Set DJANGO_SUPERUSER_EMAIL.'))
            return

        if not username:
            username = email

        User = get_user_model()
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            },
        )

        changed = False
        if getattr(user, 'username', None) != username:
            user.username = username
            changed = True

        for field, value in (('is_staff', True), ('is_superuser', True), ('is_active', True)):
            if getattr(user, field, None) != value:
                setattr(user, field, value)
                changed = True

        if created or not user.check_password(password):
            user.set_password(password)
            changed = True

        if changed:
            user.save()

        message = 'Created' if created else 'Ensured'
        self.stdout.write(self.style.SUCCESS(f'{message} superuser: {email}'))
