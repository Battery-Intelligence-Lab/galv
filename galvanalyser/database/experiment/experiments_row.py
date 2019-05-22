import psycopg2


class ExperimentsRow:
    def __init__(self, name, date, experiment_type, id=None):
        self.id = id
        self.name = name
        self.date = date
        self.experiment_type = experiment_type

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.experiments (name, date, type) "
                    "VALUES (%s, %s, %s) "
                    "RETURNING id"
                ),
                [self.name, self.date, self.experiment_type],
            )
            self.id = cursor.fetchone()[0]

    @staticmethod
    def select_from_name_and_date(name, date, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, experiment_type FROM experiment.experiments "
                    "WHERE name=(%s) AND date=(%s)"
                ),
                [name, date],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return ExperimentsRow(
                id=result[0], name=name, date=date, experiment_type=result[1]
            )
