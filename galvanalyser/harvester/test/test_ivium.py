from harvester_test_case import HarvesterTestCase
import glob
from harvester.ivium_input_file import IviumInputFile


class TestIviumFileFormat(HarvesterTestCase):
    def test_units(self):
        for filename in glob.glob(self.DATA_DIR + '/*.idf'):
            input_file = IviumInputFile(filename)
            mapping = \
                input_file.get_standard_column_to_file_column_mapping()
            self.assertGreater(len(mapping), 0)
            for i in range(100):
                row_raw = next(input_file.load_data(
                    filename, ["amps"]
                ))
                row_converted = next(
                    input_file.convert_file_cols_to_std_cols(
                        input_file.load_data(
                            filename, ["amps"]
                        ),
                        {'amps': 1}
                    ),
                )
                self.assertEqual(
                    row_raw['amps'],
                    row_converted[1]
                )

    def test_read_idf_files(self):
        for filename in glob.glob(self.DATA_DIR + '/*.idf'):
            input_file = IviumInputFile(filename)
            metadata = input_file.metadata
            task_generator = input_file.get_data_labels()
            num_tasks = sum(1 for t in task_generator)
            num_tasks_from_metadata = len(
                metadata['misc_file_data']['ivium format metadata'][0]['Tasks']
            )
            self.assertEqual(num_tasks, num_tasks_from_metadata)
            data_generator = input_file.load_data(
                filename, ["amps", "volts", "test_time"]
            )
            num_samples = sum(1 for d in data_generator)
            self.assertEqual(num_samples, metadata['num_rows'])
