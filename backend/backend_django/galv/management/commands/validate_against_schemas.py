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

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("statuses", nargs="*", type=str, default=[ValidationStatus.UNCHECKED])

        # Named (optional) arguments
        parser.add_argument(
            "--halt-on-error",
            action="store_true",
            help="Halt when an error is encountered instead of marking the validation as ERROR and continuing.",
            default=False,
        )

    def handle(self, *args, **options):
        statuses = options["statuses"]
        to_check = SchemaValidation.objects.filter(status__in=statuses)
        if len(to_check) == 0:
            self.stdout.write(f"No schema validations found with status {'|'.join(statuses)}.")
            return
        self.stdout.write(f"Found {len(to_check)} schema validations with status {'|'.join(statuses)}.")
        statuses = {
            ValidationStatus.VALID: 0,
            ValidationStatus.INVALID: 0,
            ValidationStatus.SKIPPED: 0,
            ValidationStatus.ERROR: 0,
            ValidationStatus.UNCHECKED: 0,
        }
        for sv in to_check:
            sv.validate(halt_on_error=options["halt_on_error"])
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
