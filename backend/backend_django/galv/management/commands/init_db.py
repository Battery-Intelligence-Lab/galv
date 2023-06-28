# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Create timeseries_data table in database."

    def handle(self, *args, **options):
        self.stdout.write("Creating timeseries_data table... ")
        with connection.cursor() as curs:
            curs.execute("""
            CREATE TABLE IF NOT EXISTS timeseries_data (
                sample bigint NOT NULL,
                column_id bigint NOT NULL,
                value double precision NOT NULL,
                PRIMARY KEY (sample, column_id),
                FOREIGN KEY (column_id)
                    REFERENCES "galv_datacolumn" (id) MATCH SIMPLE
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            ) WITH (OIDS = FALSE)
            """)
            self.stdout.write(self.style.SUCCESS('Complete.'))
