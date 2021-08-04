from galvanalyser_test_case import GalvanalyserTestCase
import glob
from galvanalyser.harvester.biologic_input_file import BiologicMprInputFile

class TestBiologicFileFormat(GalvanalyserTestCase):
    def test_units(self):
        for filename in glob.glob(self.DATA_DIR + '/*.mpr'):
            input_file = BiologicMprInputFile(filename)
            mapping = input_file.get_columns()
            self.assertGreater(len(mapping), 0)
            self.assertEqual(input_file.convert_unit("I/mA", 1e3), 1)

    def test_read_mpr_files(self):
        for filename in glob.glob(self.DATA_DIR + '/*.mpr'):
            input_file = BiologicMprInputFile(filename)
            metadata = input_file.metadata
            task_generator = input_file.get_data_labels()
            num_tasks = sum(1 for t in task_generator)
            self.assertGreater(num_tasks, 0)
            data_generator = input_file.load_data(
                filename, ["I/mA"]
            )
            num_samples = sum(1 for d in data_generator)
            self.assertEqual(num_samples, metadata['num_rows'])

