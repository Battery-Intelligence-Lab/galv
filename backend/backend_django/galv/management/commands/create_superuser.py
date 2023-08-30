# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = """
    Create superuser with login details from envvars 
    DJANGO_SUPERUSER_USERNAME (default=admin), 
    DJANGO_SUPERUSER_PASSWORD (required)
    """

    def handle(self, *args, **options):
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', "")
        if not len(password):
            self.stdout.write(self.style.WARNING(
                'No DJANGO_SUPERUSER_PASSWORD specified, skipping superuser creation.'
            ))
            return
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f'User {username} already exists: skipping user creation.'
            ))
            return
        User.objects.create_user(
            username=username,
            password=password,
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        self.stdout.write(self.style.SUCCESS(f'Created superuser {username}.'))
