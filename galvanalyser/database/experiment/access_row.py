import psycopg2


class AccessRow:
    def __init__(self, dataset_id, user_name):
        self.dataset_id = dataset_id
        self.user_name = user_name

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.access (dataset_id, user_name) "
                    "VALUES (%s, %s) ON CONFLICT DO NOTHING"
                ),
                [self.dataset_id, self.user_name],
            )

    @staticmethod
    def select_from_dataset_id(dataset_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT user_name FROM experiment.access "
                    "WHERE dataset_id=(%s)"
                ),
                [dataset_id],
            )
            records = cursor.fetchall()
            return [
                AccessRow(dataset_id=dataset_id, user_name=result[0])
                for result in records
            ]

    @staticmethod
    def select_from_user_name(user_name, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT dataset_id FROM experiment.access "
                    "WHERE user_name=(%s)"
                ),
                [user_name],
            )
            records = cursor.fetchall()
            return [
                AccessRow(dataset_id=result[0], user_name=user_name)
                for result in records
            ]

    @staticmethod
    def current_user_has_access_to_dataset(dataset_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT count(*) from experiment.access WHERE "
                    "dataset_id = (%s) AND user_name = current_user;"
                ),
                [dataset_id],
            )
            return cursor.fetchone()[0] > 0
