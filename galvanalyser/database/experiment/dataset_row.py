import psycopg2


class DatasetRow:
    def __init__(self, name, date, dataset_type, id=None):
        self.id = id
        self.name = name
        self.date = date
        self.dataset_type = dataset_type

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.dataset (name, date, type) "
                    "VALUES (%s, %s, %s) "
                    "RETURNING id"
                ),
                [self.name, self.date, self.dataset_type],
            )
            self.id = cursor.fetchone()[0]
            # except
            # psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "dataset_pkey"
            # DETAIL:  Key (name, date)=(TPG1+-+Cell+15+-+002, 2018-02-23 08:42:16+00) already exists.

    @staticmethod
    def select_from_name_and_date(name, date, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, type FROM experiment.dataset "
                    "WHERE name=(%s) AND date=(%s)"
                ),
                [name, date],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return DatasetRow(
                id=result[0], name=name, date=date, dataset_type=result[1]
            )

    @staticmethod
    def select_all_dataset(conn):
        with conn.cursor() as cursor:
            cursor.execute(
                ("SELECT id, name, date, type " "FROM experiment.dataset")
            )
            records = cursor.fetchall()
            return [
                DatasetRow(
                    id=result[0],
                    name=result[1],
                    date=result[2],
                    dataset_type=result[3],
                )
                for result in records
            ]
