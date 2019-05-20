import psycopg2


class ObservedFilesRow:
    def __init__(
        self, harvester_id, path, last_observed_size, last_observed_time
    ):
        self.harvester_id = harvester_id
        self.path = path
        self.last_observed_size = last_observed_size
        self.last_observed_time = last_observed_time

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO harvesters.observed_files "
                    "(harvester_id, path, last_observed_size, "
                    "last_observed_time) "
                    "VALUES (%s, %s, %s, %s) ON CONFLICT DO UPDATE SET "
                    "last_observed_size = %s, last_observed_time = %s"
                ),
                [
                    self.harvester_id,
                    self.path,
                    self.last_observed_size,
                    self.last_observed_time,
                    self.last_observed_size,
                    self.last_observed_time,
                ],
            )

    @staticmethod
    def select_from_id_and_path(harvester_id, path, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT last_observed_size, last_observed_time FROM "
                    "harvesters.observed_files WHERE "
                    "harvester_id=(%s) AND path=(%s)"
                ),
                [harvester_id, path],
            )
            result = cursor.fetchone()
            return HarvestersRow(
                harvester_id,
                path,
                last_observed_size=result[0],
                last_observed_time=result[1],
            )

    @staticmethod
    def select_from_id_(harvester_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT path, last_observed_size, last_observed_time FROM "
                    "harvesters.observed_files WHERE harvester_id=(%s)"
                ),
                [harvester_id],
            )
            records = cursor.fetchall()
            return [
                HarvestersRow(
                    harvester_id,
                    path=result[0],
                    last_observed_size=result[1],
                    last_observed_time=result[2],
                )
                for result in records
            ]
