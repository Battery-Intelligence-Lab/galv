from galvanalyser_test_case import GalvanalyserTestCase
import os
from galvanalyser.database.util.battery_exceptions import UnsupportedFileTypeError
from galvanalyser.harvester.maccor_input_file import MaccorInputFile

class TestMaccorFileFormat(GalvanalyserTestCase):
    def test_units(self):
        for root, dirs, files in os.walk(self.DATA_DIR):
            for name in files:
                filename = os.path.join(root, name)
                try:
                    input_file = MaccorInputFile(filename)
                except UnsupportedFileTypeError:
                    continue

                mapping = input_file.get_columns()
                self.assertGreater(len(mapping), 0)

    def test_read_csv_files(self):
        files_found = 0
        for root, dirs, files in os.walk(self.DATA_DIR):
            for name in files:
                filename = os.path.join(root, name)
                try:
                    input_file = MaccorInputFile(filename)
                    files_found += 1
                except UnsupportedFileTypeError:
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

