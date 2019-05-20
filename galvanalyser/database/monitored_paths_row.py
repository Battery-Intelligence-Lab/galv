import psycopg2


class MonitoredPathsRow:
    def __init__(self, harvester_id, monitored_for):
        self.harvester_id = harvester_id
        self.monitored_for = monitored_for

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO harvesters.monitored_paths "
                    "(harvester_id, monitored_for) VALUES (%s, %s)"
                ),
                [self.harvester_id, self.monitored_for],
            )

    @staticmethod
    def select_from_harvester_id(harvester_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT monitored_for FROM harvesters.monitored_paths "
                    "WHERE harvester_id=(%s)"
                ),
                [harvester_id],
            )
            records = cursor.fetchall()
            return [
                MonitoredPathsRow(
                    harvester_id=harvester_id, monitored_for=result[0]
                )
                for result in records
            ]

    @staticmethod
    def select_from_monitored_for(monitored_for, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT harvester_id FROM harvesters.monitored_paths "
                    "WHERE monitored_for=(%s)"
                ),
                [monitored_for],
            )
            records = cursor.fetchall()
            return [
                MonitoredPathsRow(
                    harvester_id=result[0], monitored_for=monitored_for
                )
                for result in records
            ]
