import psycopg2
from galvanalyser.database.util.iter_file import IteratorFile
from timeit import default_timer as timer

import galvanalyser.harvester.battery_exceptions as battery_exceptions


class DataRow:
    def __init__(
        self,
        experiment_id,
        sample_no,
        time,
        voltage,
        current,
        charge,
        temperature,
    ):
        self.experiment_id = experiment_id
        self.sample_no = sample_no
        self.time = time
        self.voltage = voltage
        self.current = current
        self.charge = charge
        self.temperature = temperature

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.data (experiment_id, sample_no, "
                    '"time", voltage, current, charge) '
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)"
                ),
                [
                    self.experiment_id,
                    self.sample_no,
                    self.time,
                    self.voltage,
                    self.current,
                    self.charge,
                    self.temperature,
                ],
            )

    @staticmethod
    def insert_input_file(input_file, conn):
        required_column_names = DataRow.get_column_names(conn)
        print("Getting data")
        row_generator = input_file.get_data_row_generator(
            required_column_names
        )
        iter_file = IteratorFile(row_generator)
        with conn.cursor() as cursor:
            print("Copying data to table")
            start = timer()
            cursor.copy_from(iter_file, "experiment.data")
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
    def get_column_names(conn):
        with conn.cursor() as cursor:
            cursor.execute(("SELECT * FROM experiment.data LIMIT 0"))
            return [desc[0] for desc in cursor.description]

    @staticmethod
    def select_from_experiment_id_and_sample_no(
        experiment_id, sample_no, conn
    ):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT test_time, volts, amps, capacity, temperature "
                    "FROM experiment.data "
                    "WHERE experiment_id=(%s) AND sample_no=(%s)"
                ),
                [experiment_id, sample_no],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return DataRow(
                experiment_id=experiment_id,
                sample_no=sample_no,
                time=result[0],
                voltage=result[1],
                current=result[2],
                charge=result[3],
                temperature=result[4],
            )
