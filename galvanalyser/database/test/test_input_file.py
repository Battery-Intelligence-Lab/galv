from galvanalyser_test_case import GalvanalyserTestCase
from pygalvanalyser.experiment.input_file import InputFile
from pygalvanalyser.experiment.timeseries_data_row import TimeseriesDataRow
from pygalvanalyser.experiment.dataset_row import DatasetRow
from pygalvanalyser.experiment.institution_row import InstitutionRow
import datetime


class DummyInput(InputFile):

    data = [
        [1.0, 2.0, 3.0],
        [2.0, 3.0, 4.0],
        [3.0, 4.0, 5.0],
        [4.0, 5.0, 6.0],
        [5.0, 6.0, 7.0],
        [6.0, 7.0, 8.0],
    ]

    def __init__(self, file_path):
        super().__init__(file_path)

    def get_file_column_to_standard_column_mapping(self):
        return {"amps": 2, "volts": 3, "test_time": 1}

    def load_data(self, file_path, columns, column_renames=None):
        columns_of_interest = []
        column_names = ["test_time", "amps", "volts"]
        for col_idx, column_name in enumerate(column_names):
            if column_name in columns:
                columns_of_interest.append(col_idx)
            if column_renames is not None and column_name in column_renames:
                column_names[col_idx] = column_renames[column_name]
        for row in self.data:
            yield {
                column_names[col_idx]: row[col_idx]
                for col_idx in columns_of_interest
            }

    def get_data_labels(self):
        for item in []:
            yield item

    def load_metadata(self):
        metadata = {}
        metadata["Machine Type"] = "Dummy"
        metadata["Dataset Name"] = "Dummy1"
        metadata["Date of Test"] = datetime.datetime.now()
        columns_with_data = {
            name: {"has_data": True, "is_numeric": True}
            for name in
            self.get_file_column_to_standard_column_mapping()
        }
        metadata["num_rows"] = len(self.data)
        metadata["first_sample_no"] = 1
        metadata["last_sample_no"] = len(self.data)
        print(metadata)
        return metadata, columns_with_data

    def validate_file(self):
        return


class TestInputFile(GalvanalyserTestCase):
    def test_dummy_input(self):
        oxford = InstitutionRow.select_from_name(
            self.INSTITUTION, self.harvester_conn
        )

        dataset = DatasetRow(
            name='dummy',
            date=datetime.datetime.now(),
            institution_id=oxford.id,
            dataset_type='test',
            original_collector='test',
        )
        dataset.insert(self.harvester_conn)

        input_file = DummyInput('nofile')
        TimeseriesDataRow.insert_input_file(
            input_file, dataset.id, self.harvester_conn
        )
        latest_row = TimeseriesDataRow\
            .select_latest_by_dataset_id(dataset.id, self.harvester_conn)
        self.assertEquals(
            [6.0, 7.0, 8.0],
            [x.value for x in latest_row]
        )
