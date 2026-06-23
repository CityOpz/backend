import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a default admin user when launching the application."

    def handle(self, *args, **options):
        username = os.getenv("DEFAULT_ADMIN_USERNAME")
        email = os.getenv("DEFAULT_ADMIN_EMAIL")
        password = os.getenv("DEFAULT_ADMIN_PASSWORD")
        role = os.getenv("DEFAULT_ADMIN_ROLE", "ADMIN")

        if not username or not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Default admin was not created because one or more environment variables are missing"
                )
            )
            return

        user_model = get_user_model()

        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={"email": email, "role": role, "is_active": True},
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"Admin user '{username}' created successfully.")
            )

        self.stdout.write(self.style.SUCCESS("Admin seed completed successfully."))
