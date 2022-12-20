
class AccessRow:
    def __init__(self, dataset_id, user_id):
        self.dataset_id = dataset_id
        self.user_id = user_id

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.access (dataset_id, user_id) "
                    "VALUES (%s, %s) ON CONFLICT DO NOTHING"
                ),
                [self.dataset_id, self.user_id],
            )

    @staticmethod
    def exists(dataset_id, user_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT COUNT(1) "
                    "FROM experiment.access "
                    "WHERE dataset_id=(%s) AND user_id=(%s)"
                ),
                [dataset_id, user_id],
            )
            result = cursor.fetchone()
            return bool(result)

    @staticmethod
    def select_from_dataset_id(dataset_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT user_id FROM experiment.access "
                    "WHERE dataset_id=(%s)"
                ),
                [dataset_id],
            )
            records = cursor.fetchall()
            return [
                AccessRow(dataset_id=dataset_id, user_id=result[0])
                for result in records
            ]

    @staticmethod
    def select_from_user_id(user_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT dataset_id FROM experiment.access "
                    "WHERE user_id=(%s)"
                ),
                [user_id],
            )
            records = cursor.fetchall()
            return [
                AccessRow(dataset_id=result[0], user_id=user_id)
                for result in records
            ]
