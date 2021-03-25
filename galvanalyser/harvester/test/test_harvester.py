from harvester_test_case import HarvesterTestCase
from timeit import default_timer as timer
import harvester.__main__ as harvester
from pygalvanalyser.harvester.harvester_row import HarvesterRow
from pygalvanalyser.harvester.monitored_path_row import MonitoredPathRow
from pygalvanalyser.harvester.observed_file_row import ObservedFileRow
from pygalvanalyser.experiment.dataset_row import DatasetRow

import os
import json
from datetime import datetime, timezone, timedelta



class TestHarvester(HarvesterTestCase):
    # well capture all the filename that failed here
    def setUp(self):
        self.verificationErrors = []

    # if any files failed, print errors here
    def tearDown(self):
        self.maxDiff = None
        self.assertEqual([], self.verificationErrors)

    def test_main(self):
        template = {
            "database_username": self.HARVESTER,
            "database_password": self.HARVESTER_PWD,
            "database_host": "galvanalyser_postgres",
            "database_port": 5433,
            "database_name": self.DATABASE,
            "machine_id": self.MACHINE_ID,
            "institution": self.HARVESTER_INSTITUTION,
        }
        if not os.path.exists('./config'):
            os.makedirs('./config')

        with open('./config/harvester-config.json', "w+") as json_file:
            json.dump(template, json_file, indent=4)

        harvester.main(None)

        # should have added files to database
        harvester_row = HarvesterRow.select_from_machine_id(
            self.MACHINE_ID,
            self.conn
        )
        self.assertIsNotNone(harvester_row)

        monitor_path = \
            MonitoredPathRow.select_from_harvester_id_and_path(
                harvester_row.id,
                self.DATA_DIR,
                self.conn
            )
        self.assertIsNotNone(monitor_path)
        file = ObservedFileRow.select_from_id_(
                    monitor_path.monitor_path_id,
                    self.conn
                )
        # check all files are in, then mark them stable for > 1 min
        for root, dirs, files in os.walk(self.DATA_DIR):
            for name in files:
                # check that filename is in list of files
                print(name)
                file = ObservedFileRow.select_from_id_and_path(
                    monitor_path.monitor_path_id,
                    name,
                    self.conn
                )
                self.assertIsNotNone(file)

                file.file_state = 'STABLE'
                file.last_observed_time = \
                    datetime.now(timezone.utc) - timedelta(minutes=1),
                file.insert(self.conn)
            break
        self.conn.commit()


        # files are now stable, rerun main to insert them
        harvester.main(None)

        # check that they are all inserted successfully
        for root, dirs, files in os.walk(self.DATA_DIR):
            for name in files:
                file = ObservedFileRow.select_from_id_and_path(
                    monitor_path.monitor_path_id,
                    name,
                    self.conn
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



