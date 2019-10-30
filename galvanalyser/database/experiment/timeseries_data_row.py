import psycopg2
from galvanalyser.database.util.iter_file import IteratorFile
from timeit import default_timer as timer

import galvanalyser.harvester.battery_exceptions as battery_exceptions


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
    def insert_input_file(input_file, conn):
        required_column_names = TimeseriesDataRow.get_column_names(conn)
        print("Getting data")
        row_generator = input_file.get_data_row_generator(
            required_column_names
        )
        iter_file = IteratorFile(row_generator)
        with conn.cursor() as cursor:
            print("Copying data to table")
            start = timer()
            cursor.copy_from(iter_file, "experiment.timeseries_data")
            end = timer()
            if cursor.rowcount != input_file.metadata["num_rows"]:
                raise battery_exceptions.InsertError(
                    "Insert failed. Inserted {} of {} rows before failure".format(
                        cursor.rowcount, input_file.metadata["num_rows"]
                    )
                )
            print("Done copying data to table")
            print(
                "Inserted {} rows in {:.2f} seconds".format(
                    cursor.rowcount, end - start
                )
            )

    @staticmethod
    def select_from_dataset_id_and_sample_no(
        dataset_id, sample_no, conn
    ):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT test_time, volts, amps, capacity, temperature "
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
