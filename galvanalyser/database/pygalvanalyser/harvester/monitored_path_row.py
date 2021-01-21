import psycopg2


class MonitoredPathRow:
    def __init__(
        self, harvester_id, monitored_for, path, monitor_path_id=None
    ):
        self.harvester_id = harvester_id
        self.monitored_for = monitored_for
        self.path = path
        self.monitor_path_id = monitor_path_id

    def __str__(self):
        return (
            'MonitoredPathRow(harvester_id={}, monitored_for={} '
            'path={}, monitor_path_id={})'
        ).format(
            self.harvester_id,
            self.monitored_for,
            self.path,
            self.monitor_path_id
        )

    def insert(self, conn):
        # TODO change this to an upsert
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO harvesters.monitored_path "
                    "(harvester_id, monitored_for, path) VALUES (%s, %s, %s)"
                ),
                [self.harvester_id, self.monitored_for, self.path],
            )

    @staticmethod
    def select_from_harvester_id(harvester_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT monitored_for, path, monitor_path_id FROM "
                    "harvesters.monitored_path "
                    "WHERE harvester_id=(%s)"
                ),
                [harvester_id],
            )
            records = cursor.fetchall()
            return [
                MonitoredPathRow(
                    harvester_id=harvester_id,
                    monitored_for=result[0],
                    path=result[1],
                    monitor_path_id=result[2],
                )
                for result in records
            ]

    @staticmethod
    def select_from_harvester_id_and_path(harvester_id, path, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT monitored_for, monitor_path_id FROM "
                    "harvesters.monitored_path "
                    "WHERE harvester_id=(%s) AND path=(%s)"
                ),
                [harvester_id, path],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return MonitoredPathRow(
                    harvester_id=harvester_id,
                    monitored_for=result[0],
                    path=path,
                    monitor_path_id=result[1],
                )

    @staticmethod
    def select_from_monitored_for(monitored_for, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT harvester_id, path, monitor_path_id FROM "
                    "harvesters.monitored_path "
                    "WHERE monitored_for=(%s)"
                ),
                [monitored_for],
            )
            records = cursor.fetchall()
            return [
                MonitoredPathRow(
                    harvester_id=result[0],
                    monitored_for=monitored_for,
                    path=result[1],
                    monitor_path_id=result[2],
                )
                for result in records
            ]
