import psycopg2
from galvanalyser.harvester.input_file import InputFile


class DataRow:
    def __init__(
        self, experiment_id, sample_no, time, voltage, current, charge
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
        pass


    @staticmethod
    def get_column_names(conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT * FROM experiment.data LIMIT 0"
                ))
            return [desc[0] for desc in cursor.description]

#    @staticmethod
#    def select_from_name_and_date(name, date, conn):
#        with conn.cursor() as cursor:
#            cursor.execute(
#                (
#                    "SELECT id, experiment_type FROM experiment.experiments "
#                    "WHERE name=(%s) AND date=(%s)"
#                ),
#                [name, date],
#            )
#            result = cursor.fetchone()
#            if result is None:
#                return None
#            return ExperimentsRow(
#                id=result[0], name=name, date=date, experiment_type=result[1]
#            )
