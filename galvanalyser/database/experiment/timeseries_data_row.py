import psycopg2
from galvanalyser.database.util.iter_file import IteratorFile
from timeit import default_timer as timer

from galvanalyser.database.experiment.column_row import ColumnRow

import galvanalyser.harvester.battery_exceptions as battery_exceptions

RECORD_NO_COLUMN_ID = 0
TEST_TIME_COLUMN_ID = 1

class TimeseriesDataRow:
    def __init__(
        self,
        dataset_id,
        sample_no,
        column_id,
        value,
    ):
        self.dataset_id = dataset_id
        self.sample_no = sample_no
        self.column_id = column_id
        self.value = value

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.timeseries_data "
                    "(dataset_id, sample_no, column_id, value) "
                    "VALUES (%s, %s, %s, %s)"
                ),
                [
                    self.dataset_id,
                    self.sample_no,
                    self.column_id,
                    self.value,
                ],
            )

    @staticmethod
    def insert_input_file(input_file, dataset_id, conn, standard_cols_to_file_cols=None):
        if standard_cols_to_file_cols is None:
            standard_cols_to_file_cols = {}
        required_column_ids = {RECORD_NO_COLUMN_ID, TEST_TIME_COLUMN_ID}

        builtin_std_cols_to_file_cols = input_file.get_standard_column_to_file_column_mapping()
        # override builtin definitions with external ones if provided
        builtin_std_cols_to_file_cols.update(standard_cols_to_file_cols)
        standard_cols_to_file_cols = builtin_std_cols_to_file_cols

        # Check if we need to create new column types
        unknown_column_names = input_file.get_unknown_numeric_columns_with_data_names(standard_cols_to_file_cols)
        for name in unknown_column_names:
            col = ColumnRow.select_one_unknown_with_name(name, conn)
            if col is None:
                new_column = ColumnRow(-1, name)
                new_column.insert(conn)
                standard_cols_to_file_cols[new_column.id] = name
            else:
                standard_cols_to_file_cols[col.id] = name
        
        # Get all numeric data from the file
        numeric_file_cols_with_data = input_file.get_names_of_numeric_columns_with_data()
        for standard_id, file_col_name in standard_cols_to_file_cols.items():
            if file_col_name in numeric_file_cols_with_data:
                required_column_ids.add(standard_id)

        print("Getting data")
        row_generator = input_file.get_data_row_generator(
            list(required_column_ids), dataset_id, RECORD_NO_COLUMN_ID, standard_cols_to_file_cols
        )
        iter_file = IteratorFile(row_generator)
        num_value_columns = len(required_column_ids)-1
        expected_insert_count = input_file.metadata["num_rows"] * num_value_columns
        with conn.cursor() as cursor:
            print("Copying data to table")
            start = timer()
            cursor.copy_from(iter_file, "experiment.timeseries_data")
            end = timer()
            if cursor.rowcount != expected_insert_count:
                raise battery_exceptions.InsertError(
                    "Insert failed. Inserted {} of {} values ({} rows * {} columns) before failure".format(
                        cursor.rowcount,
                        expected_insert_count,
                        input_file.metadata["num_rows"],
                        num_value_columns
                    )
                )
            print("Done copying data to table")
            print(
                "Inserted {} rows in {:.2f} seconds".format(
                    cursor.rowcount, end - start
                )
            )

    @staticmethod
    def select_one_from_dataset_id_and_sample_no(
        dataset_id, sample_no, conn
    ):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT column_id, value "
                    "FROM experiment.timeseries_data "
                    "WHERE dataset_id=(%s) AND sample_no=(%s) "
                    "LIMIT 1"
                ),
                [dataset_id, sample_no],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return TimeseriesDataRow(
                dataset_id=dataset_id,
                sample_no=sample_no,
                column_id=result[0],
                value=result[1],
            )
