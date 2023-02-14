from test_case import GalvanalyserTestCase
from timeit import default_timer as timer
import galvanalyser.harvester as harvester
from galvanalyser.database.harvester import (
    HarvesterRow,
    MonitoredPathRow,
    ObservedFileRow,
)
from galvanalyser.database.experiment import DatasetRow

import os
import json
from datetime import datetime, timezone, timedelta
import unittest



class TestHarvester(GalvanalyserTestCase):
    # well capture all the filename that failed here
    def setUp(self):
        self.verificationErrors = []

    # if any files failed, print errors here
    def tearDown(self):
        self.maxDiff = None
        self.assertEqual([], self.verificationErrors)

    def test_main(self):
        harvester.main(
            database_user=self.HARVESTER,
            database_password=self.HARVESTER_PWD,
            machine_id=self.MACHINE_ID,
            database_host="postgres",
            database_port=5433,
            database_name=self.DATABASE,
            base_path=None
        )

        # should have added files to database
        harvester_row = HarvesterRow.select_from_machine_id(
            self.MACHINE_ID,
            self.harvester_conn
        )
        self.assertIsNotNone(harvester_row)

        monitor_path = \
            MonitoredPathRow.select_from_harvester_id_and_path(
                harvester_row.id,
                self.DATA_DIR,
                self.harvester_conn
            )
        self.assertIsNotNone(monitor_path)
        file = ObservedFileRow.select_from_id_(
                    monitor_path.id,
                    self.harvester_conn
                )
        # check all files are in, then mark them stable for > 1 min
        for root, dirs, files in os.walk(self.DATA_DIR):
            for name in files:
                # check that filename is in list of files
                relname = os.path.relpath(os.path.join(root, name), self.DATA_DIR)
                file = ObservedFileRow.select_from_id_and_path(
                    monitor_path.id,
                    relname,
                    self.harvester_conn
                )
                self.assertIsNotNone(file)

                file.file_state = 'STABLE'
                file.last_observed_time = \
                    datetime.now(timezone.utc) - timedelta(minutes=1),
                file.insert(self.harvester_conn)
        self.harvester_conn.commit()


        # files are now stable, rerun main to insert them
        harvester.main(
            database_user=self.HARVESTER,
            database_password=self.HARVESTER_PWD,
            machine_id=self.MACHINE_ID,
            database_host="postgres",
            database_port=5433,
            database_name=self.DATABASE,
            base_path=None
        )

        # check that they are all inserted successfully
        for root, dirs, files in os.walk(self.DATA_DIR):
            for name in files:
                relname = os.path.relpath(os.path.join(root, name), self.DATA_DIR)
                file = ObservedFileRow.select_from_id_and_path(
                    monitor_path.id,
                    relname,
                    self.harvester_conn
                )
                self.assertIsNotNone(file)
                try:
                    self.assertEqual(file.file_state, 'IMPORTED')
                except AssertionError as e:
                    self.verificationErrors.append(
                        'filename = {}, error = {}'.format(name, e)
                    )


if __name__ == '__main__':
    unittest.main()



