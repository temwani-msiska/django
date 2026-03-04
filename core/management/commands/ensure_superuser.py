import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create/update a superuser from environment variables if provided.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not password or (not username and not email):
            self.stdout.write(
                self.style.WARNING(
                    'Skipping superuser creation. Set DJANGO_SUPERUSER_PASSWORD and either DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_EMAIL.'
                )
            )
            return

        User = get_user_model()
        lookup_field = 'username' if username else 'email'
        lookup_value = username or email

        defaults = {
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }
        if email:
            defaults['email'] = email

        user, created = User.objects.get_or_create(**{lookup_field: lookup_value}, defaults=defaults)

        updated = False
        for field, value in defaults.items():
            if getattr(user, field, None) != value:
                setattr(user, field, value)
                updated = True

        if email and getattr(user, 'email', None) != email:
            user.email = email
            updated = True

        if created or not user.check_password(password):
            user.set_password(password)
            updated = True

        if updated:
            user.save()

        message = 'Created' if created else 'Ensured'
        self.stdout.write(self.style.SUCCESS(f'{message} superuser: {lookup_value}'))
