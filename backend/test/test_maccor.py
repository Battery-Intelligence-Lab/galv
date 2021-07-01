from harvester_test_case import HarvesterTestCase
import glob
import pygalvanalyser.util.battery_exceptions as battery_exceptions
from harvester.maccor_input_file import MaccorInputFile

class TestMaccorFileFormat(HarvesterTestCase):
    def test_units(self):
        for filename in glob.glob(self.DATA_DIR + '/*'):
            try:
                input_file = MaccorInputFile(filename)
            except battery_exceptions.UnsupportedFileTypeError:
                continue

            mapping = \
                input_file.get_standard_column_to_file_column_mapping()
            self.assertGreater(len(mapping), 0)

    def test_read_csv_files(self):
        files_found = 0
        for filename in glob.glob(self.DATA_DIR + '/*'):
            try:
                input_file = MaccorInputFile(filename)
                files_found += 1
            except battery_exceptions.UnsupportedFileTypeError:
                continue
            metadata = input_file.metadata
            task_generator = input_file.get_data_labels()
            num_tasks = sum(1 for t in task_generator)
            self.assertGreater(num_tasks, 0)
            data_generator = input_file.load_data(
                filename, ["Amps", "Volts"]
            )
            num_samples = sum(1 for d in data_generator)
            self.assertEqual(num_samples, metadata['num_rows'])
        self.assertGreater(files_found, 0)

