import psycopg2


class AccessRow:
    def __init__(self, experiment_id, user_name):
        self.experiment_id = experiment_id
        self.user_name = user_name

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.access (experiment_id, user_name) "
                    "VALUES (%s, %s) ON CONFLICT DO NOTHING"
                ),
                [self.experiment_id, self.user_name],
            )

    @staticmethod
    def select_from_experiment_id(experiment_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT user_name FROM experiment.access "
                    "WHERE experiment_id=(%s)"
                ),
                [experiment_id],
            )
            records = cursor.fetchall()
            return [
                AccessRow(experiment_id=experiment_id, user_name=result[0])
                for result in records
            ]

    @staticmethod
    def select_from_user_name(user_name, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT experiment_id FROM experiment.access "
                    "WHERE user_name=(%s)"
                ),
                [user_name],
            )
            records = cursor.fetchall()
            return [
                AccessRow(experiment_id=result[0], user_name=user_name)
                for result in records
            ]
