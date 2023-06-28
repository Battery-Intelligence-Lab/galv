# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
from unittest.mock import patch
import os
from pathlib import Path

from harvester.harvester.parse.input_file import InputFile
import harvester.harvester.run
import harvester.harvester.harvest

def get_test_file_path():
    return os.getenv('TEST_DIR', "/usr/test_data")

class ConfigResponse:
    status_code = 200

    def json(self):
        return {
            "url": "http://app/harvesters/1/",
            "id": 1,
            "api_key": "galv_hrv_x",
            "name": "Test Harvester",
            "sleep_time": 0,
            "monitored_paths": [
                {
                    "path": get_test_file_path(),
                    "stable_time": 0,
                    "regex": "^(?!.*\\.skip$).*$",
                }
            ],
            "standard_units": [
                {
                    "id": 1,
                    "name": "Unitless"
                },
                {
                    "id": 2,
                    "name": "Time"
                },
                {
                    "id": 3,
                    "name": "Volts"
                },
                {
                    "id": 4,
                    "name": "Amps"
                },
                {
                    "id": 5,
                    "name": "Energy"
                },
                {
                    "id": 6,
                    "name": "Charge"
                },
                {
                    "id": 7,
                    "name": "Temperature"
                },
                {
                    "id": 8,
                    "name": "Power"
                },
                {
                    "id": 9,
                    "name": "Ohm"
                },
                {
                    "id": 10,
                    "name": "Degrees"
                },
                {
                    "id": 11,
                    "name": "Frequency"
                }
            ],
            "standard_columns": [
                {
                    "id": 1,
                    "name": "Unknown",
                    "unit": None
                },
                {
                    "id": 2,
                    "name": "Sample Number",
                    "unit": "http://app/units/1/"
                },
                {
                    "id": 3,
                    "name": "Time",
                    "unit": "http://app/units/2/"
                },
                {
                    "id": 4,
                    "name": "Volts",
                    "unit": "http://app/units/3/"
                },
                {
                    "id": 5,
                    "name": "Amps",
                    "unit": "http://app/units/4/"
                },
                {
                    "id": 6,
                    "name": "Energy Capacity",
                    "unit": "http://app/units/5/"
                },
                {
                    "id": 7,
                    "name": "Charge Capacity",
                    "unit": "http://app/units/6/"
                },
                {
                    "id": 8,
                    "name": "Temperature",
                    "unit": "http://app/units/7/"
                },
                {
                    "id": 9,
                    "name": "Step Time",
                    "unit": "http://app/units/8/"
                },
                {
                    "id": 10,
                    "name": "Impedence Magnitude",
                    "unit": "http://app/units/9/"
                },
                {
                    "id": 11,
                    "name": "Impedence Phase",
                    "unit": "http://app/units/10/"
                },
                {
                    "id": 12,
                    "name": "Frequency",
                    "unit": "http://app/units/11/"
                }
            ],
            "max_upload_bytes": 2621440
        }


class JSONResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self.ok = 200 <= self.status_code < 400
        self.json_data = json_data if json_data else {}

    def json(self):
        return self.json_data


def fail(e, *kwargs):
    raise Exception(e)


class TestHarvester(unittest.TestCase):
    @patch('requests.get')
    @patch('harvester.harvester.api.logger')
    @patch('harvester.harvester.run.logger')
    @patch('harvester.harvester.api.get_settings_file')
    @patch('harvester.harvester.settings.get_settings_file')
    @patch('harvester.harvester.settings.get_logfile')
    def test_config_update(
            self,
            mock_settings_log,
            mock_settings_file,
            mock_api_settings_file,
            mock_run_logger,
            mock_api_logger,
            mock_get
    ):
        mock_settings_log.return_value = '/tmp/harvester.log'
        mock_settings_file.return_value = '/tmp/harvester.json'
        mock_api_settings_file.return_value = '/tmp/harvester.json'
        mock_api_logger.error = fail
        mock_run_logger.error = fail
        mock_get.return_value = ConfigResponse()
        harvester.harvester.run.update_config()
        if not os.path.isfile(mock_settings_file()):
            raise AssertionError(f"Expected JSON file '{mock_settings_file()}' not found")

        os.remove(mock_settings_file())

    @patch('harvester.harvester.run.report_harvest_result')
    @patch('harvester.harvester.run.import_file')
    @patch('harvester.harvester.run.logger')
    def test_harvest_path(self, mock_logger, mock_import, mock_report):
        # Create an unparsable file in the test set
        Path(os.path.join(get_test_file_path(), 'unparsable.foo')).touch(exist_ok=True)
        Path(os.path.join(get_test_file_path(), 'skipped_by_regex.skip')).touch(exist_ok=True)
        mock_logger.error = fail
        mock_report.return_value = JSONResponse(200, {'state': 'STABLE'})
        mock_import.return_value = True
        harvester.harvester.run.harvest_path(Path(get_test_file_path()))
        files = []
        for c in mock_import.call_args_list:
            if c.args[1] not in files:
                files.append(c.args[1])
        if len(files) != 5:
            raise AssertionError(f"Did not find 5 files in path {get_test_file_path()}")
        for f in files:
            for task in ['file_size', 'import']:
                ok = False
                for c in mock_report.call_args_list:
                    if c.kwargs['content']['task'] == task:
                        if not task == 'import' or c.kwargs['content']['status'] == 'complete':
                            ok = True
                            break
                if not ok:
                    raise AssertionError(f"{f} did not make call with 'task'={task}")

    @patch('harvester.harvester.harvest.report_harvest_result')
    @patch('harvester.harvester.harvest.logger')
    @patch('harvester.harvester.settings.get_settings')
    def import_file(self, filename, mock_settings, mock_logger, mock_report):
        mock_settings.return_value = ConfigResponse().json()
        mock_logger.error = fail
        mock_report.return_value = JSONResponse(
            200, {'upload_info': {'last_record_number': 0, 'columns': []}}
        )
        if not harvester.harvester.harvest.import_file(get_test_file_path(), filename):
            raise AssertionError(f"Import failed for {get_test_file_path()}/{filename}")
        self.validate_report_calls(mock_report.call_args_list)

    def validate_report_calls(self, calls):
        begun = False
        for c in calls:
            if not 'content' in c.kwargs:
                raise AssertionError(f"Report made with no content")
            if not begun:
                if c.kwargs['content']['status'] != 'begin':
                    raise AssertionError(f"Expected result reports to start with status='begin'")
                if 'core_metadata' not in c.kwargs['content']:
                    raise AssertionError(f"Expected result report to contain core_metadata")
                begun = True
                continue
            if c.kwargs['content']['status'] != 'in_progress':
                raise AssertionError(f"Expected result report status to be 'in_progress'")
            if not c.kwargs['content']['data']:
                raise AssertionError(f"Expected result report to contain 'data'")
            row = c.kwargs['content']['data'][0]
            if not 'values' in row:
                raise AssertionError(f"'data' contains no 'values' field")

    def test_import_mpr(self):
        self.import_file('adam_3_C05.mpr')

    def test_import_idf(self):
        self.import_file('Ivium_Cell+1.idf')

    # def test_import_txt(self):
    #     self.import_file('TPG1+-+Cell+15+-+002.txt')


if __name__ == '__main__':
    unittest.main()
