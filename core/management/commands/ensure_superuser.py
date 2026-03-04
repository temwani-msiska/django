import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Create/update a superuser from environment variables if provided.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '').strip().lower()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stdout.write(self.style.WARNING('Skipping superuser creation. Set DJANGO_SUPERUSER_PASSWORD.'))
            return

        if not email and '@' in username:
            email = username.lower()

        if not email:
            self.stdout.write(self.style.WARNING('Skipping superuser creation. Set DJANGO_SUPERUSER_EMAIL.'))
            return

        if not username:
            username = email

        User = get_user_model()

        # Resolve an existing account first by email (case-insensitive), then username.
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            user = User.objects.filter(username=username).first() or User.objects.filter(username__iexact=username).first()

        created = False
        if user is None:
            try:
                user = User.objects.create(
                    email=email,
                    username=username,
                    is_staff=True,
                    is_superuser=True,
                    is_active=True,
                )
                created = True
            except IntegrityError:
                # Another row may already exist for username/email in a different casing.
                user = User.objects.filter(email__iexact=email).first()
                if user is None:
                    user = User.objects.filter(username=username).first() or User.objects.filter(username__iexact=username).first()
                if user is None:
                    raise

        changed = False
        if getattr(user, 'email', '').lower() != email:
            user.email = email
            changed = True

        # Only set username if it doesn't conflict with another user.
        if getattr(user, 'username', None) != username:
            conflict = User.objects.filter(username=username).exclude(pk=user.pk).exists()
            if not conflict:
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
