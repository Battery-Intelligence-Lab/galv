import psycopg2
from galvanalyser.database.util.iter_file import IteratorFile
from timeit import default_timer as timer

from galvanalyser.database.experiment import ColumnRow

import galvanalyser.database.util.battery_exceptions as battery_exceptions

RECORD_NO_COLUMN_ID = 0
TEST_TIME_COLUMN_ID = 1
VOLTAGE_COLUMN_ID = 2
AMPS_COLUMN_ID = 3
ENERGY_CAPACITY_COLUMN_ID = 4
CHARGE_CAPACITY_COLUMN_ID = 5
TEMPERATURE_COLUMN_ID = 6
STEP_TIME_COLUMN_ID = 7
IMPEDENCE_MAG_COLUMN_ID = 8
IMPEDENCE_PHASE_COLUMN_ID = 9
FREQUENCY_COLUMN_ID = 10

UNIT_UNITLESS = 0
UNIT_SECONDS = 1
UNIT_VOLTS = 2
UNIT_AMPS = 3
UNIT_WATT_HOURS = 4
UNIT_AMP_HOURS = 5
UNIT_CENTIGRADE = 6
UNIT_WATTS = 7
UNIT_OHMS = 8
UNIT_DEGREES = 9
UNIT_HERTZ = 10

class TimeseriesDataRow:
    def __init__(self, sample_no, column_id, value, column_type_id=None):
        self.sample_no = sample_no
        self.column_id = column_id
        self.column_type_id = column_type_id
        self.value = value

    def __str__(self):
        return (
            'TimeseriesDataRow(sample_no={} '
            'column_id={}, value={})'
        ).format(
            self.sample_no,
            self.column_id,
            self.value
        )

    def __repr__(self):
        return self.__str__()

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.timeseries_data "
                    "(sample_no, column_id, value) "
                    "VALUES (, %s, %s, %s)"
                ),
                [self.sample_no, self.column_id, self.value],
            )

    @staticmethod
    def insert_input_file(
        input_file,
        dataset_id,
        conn,
        last_values=None,
    ):
        column_name_to_id = {}
        # create mapping from col id to col name, creating new columns as
        # appropriate
        columns = input_file.get_columns()
        for name, type_id in columns:
            col = ColumnRow.select_from_dataset_with_name(
                dataset_id, name, conn
            )
            if col is None:
                col = ColumnRow(
                    dataset_id=dataset_id,
                    type_id=type_id,
                    name=name
                )
                col.insert(conn)
            column_name_to_id[name] = col.id

        print("Getting data")
        row_generator = input_file.get_data_row_generator(
            column_name_to_id,
            last_values,
        )
        iter_file = IteratorFile(row_generator)
        num_value_columns = len(columns)
        start_row = 0 if last_values is None else last_values[0].sample_no
        num_rows_to_insert = input_file.metadata["num_rows"] - start_row
        expected_insert_count = num_rows_to_insert * num_value_columns
        with conn.cursor() as cursor:
            print("Copying data to table")
            start = timer()
            cursor.copy_expert(
                'COPY experiment.timeseries_data FROM STDIN', iter_file
            )
            end = timer()
            if cursor.rowcount != expected_insert_count:
                raise battery_exceptions.InsertError(
                    "Insert failed. Inserted {} of {} values ({} rows * {} columns) before failure".format(
                        cursor.rowcount,
                        expected_insert_count,
                        num_rows_to_insert,
                        num_value_columns,
                    )
                )
            print("Done copying data to table")
            print(
                "Inserted {} rows ({} sample sets) in {:.2f} seconds".format(
                    cursor.rowcount, num_rows_to_insert, end - start
                )
            )

    @staticmethod
    def select_one_from_dataset_id_and_sample_no(dataset_id, sample_no, conn):
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

    @staticmethod
    def get_column_type_id(col_id, cursor):
        cursor.execute(
            (
                "SELECT type_id "
                'FROM experiment."column" '
                "WHERE id=(%s)"
                ""
            ),
            [col_id],
        )
        return cursor.fetchone()[0]

    @staticmethod
    def select_latest_by_dataset_id(dataset_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT sample_no, column_id, value "
                    "FROM experiment.timeseries_data "
                    "WHERE sample_no IN ( "
                    "SELECT sample_no from experiment.timeseries_data "
                    "WHERE column_id IN ( "
                    'SELECT id FROM experiment."column" WHERE '
                    "dataset_id=(%s)) ORDER BY sample_no DESC LIMIT 1) "
                ),
                [dataset_id],
            )
            records = cursor.fetchall()
            return [
                TimeseriesDataRow(
                    sample_no=result[0],
                    column_id=result[1],
                    column_type_id=TimeseriesDataRow.get_column_type_id(
                        result[1], cursor
                    ),
                    value=result[2],
                )
                for result in records
            ]
