from harvester_test_case import HarvesterTestCase
import glob
from harvester.biologic_input_file import BiologicMprInputFile

class TestBiologicFileFormat(HarvesterTestCase):
    def test_units(self):
        for filename in glob.glob(self.DATA_DIR + '/*.mpr'):
            input_file = BiologicMprInputFile(filename)
            mapping = \
                input_file.get_standard_column_to_file_column_mapping()
            self.assertGreater(len(mapping), 0)
            for i in range(100):
                row_raw = next(input_file.load_data(
                    filename, ["I/mA"]
                ))
                row_converted = next(input_file.convert_units(
                    input_file.load_data(
                        filename, ["I/mA"]
                    )
                ))
                self.assertEqual(
                    1e-3 * row_raw['I/mA'],
                    row_converted['I/mA']
                )

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

