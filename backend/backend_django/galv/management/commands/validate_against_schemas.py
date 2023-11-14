# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import datetime

from django.core.management.base import BaseCommand
from galv.models import SchemaValidation, ValidationStatus


class Command(BaseCommand):
    """
    Call via a CRON job.
    If this is too slow and rubbish, we can implement it with celery.
    """
    help = """
    Trawl the database and update any UNCHECKED schema validations by running their validation.
    """

    def handle(self, *args, **options):
        to_check = SchemaValidation.objects.filter(status=ValidationStatus.UNCHECKED)
        if len(to_check) == 0:
            self.stdout.write(f"No UNCHECKED schema validations found.")
            return
        self.stdout.write(f"Found {len(to_check)} UNCHECKED schema validations.")
        statuses = {
            ValidationStatus.VALID: 0,
            ValidationStatus.INVALID: 0,
            ValidationStatus.SKIPPED: 0,
            ValidationStatus.ERROR: 0,
        }
        for sv in to_check:
            sv.validate()
            sv.save()
            statuses[sv.status] += 1

        self.stdout.write(self.style.SUCCESS(f"Finished checking schema validations."))
        if statuses[ValidationStatus.ERROR]:
            self.stdout.write(self.style.ERROR(f"ERROR: {statuses[ValidationStatus.ERROR]}"))
        if statuses[ValidationStatus.VALID]:
            self.stdout.write(self.style.SUCCESS(f"VALID: {statuses[ValidationStatus.VALID]}"))
        if statuses[ValidationStatus.INVALID]:
            self.stdout.write(self.style.WARNING(f"INVALID: {statuses[ValidationStatus.INVALID]}"))
        if statuses[ValidationStatus.SKIPPED]:
            self.stdout.write(f"SKIPPED: {statuses[ValidationStatus.SKIPPED]}")
