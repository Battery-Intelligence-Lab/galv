from galvanalyser_test_case import GalvanalyserTestCase
import glob
from galvanalyser.harvester.ivium_input_file import IviumInputFile


class TestIviumFileFormat(GalvanalyserTestCase):
    def test_units(self):
        for filename in glob.glob(self.DATA_DIR + '/*.idf'):
            input_file = IviumInputFile(filename)
            mapping = input_file.get_columns()
            self.assertGreater(len(mapping), 0)
            self.assertEqual(input_file.convert_unit("amps", 1), 1)

    def test_read_idf_files(self):
        for filename in glob.glob(self.DATA_DIR + '/*.idf'):
            input_file = IviumInputFile(filename)
            metadata = input_file.metadata
            task_generator = input_file.get_data_labels()
            num_tasks = sum(1 for t in task_generator)
            num_tasks_from_metadata = len(
                metadata['misc_file_data']['Tasks']
            )
            self.assertEqual(num_tasks, num_tasks_from_metadata)
            data_generator = input_file.load_data(
                filename, ["amps", "volts", "test_time"]
            )
            num_samples = sum(1 for d in data_generator)
            self.assertEqual(num_samples, metadata['num_rows'])
