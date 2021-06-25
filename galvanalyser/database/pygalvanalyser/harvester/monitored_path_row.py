import psycopg2
import json
import pygalvanalyser


class MonitoredPathRow(pygalvanalyser.Row):
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

    def to_dict(self):
        obj = {
            'harvester_id': self.harvester_id,
            'monitored_for': self.monitored_for,
            'path': self.path,
            'monitor_path_id': self.monitor_path_id,
        }
        return obj

    def _insert_monitored_paths(self, cursor):
        if len(self.monitored_for) > 0:
            monitored_for_rows = ', '.join(
                ['({}, {})'.format(self.monitor_path_id, uid)
                    for uid in self.monitored_for]
            )
            print('XXXXX', monitored_for_rows)
            cursor.execute(
                (
                    "INSERT INTO harvesters.monitored_for "
                    "(path_id, user_id) VALUES %s"
                ),
                [monitored_for_rows],
            )

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO harvesters.monitored_path "
                    "(harvester_id, path) VALUES (%s, %s) "
                    "RETURNING monitor_path_id"
                ),
                [self.harvester_id, self.path],
            )
            self.monitor_path_id = cursor.fetchone()[0]

            self._insert_monitored_paths(cursor)


    def update(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "UPDATE harvesters.monitored_path SET "
                    "harvester_id = (%s), "
                    "path = (%s) "
                    "WHERE monitor_path_id=(%s)"
                ),
                [
                    self.harvester_id,
                    self.path, self.monitor_path_id
                ],
            )
            cursor.execute(
                (
                    "DELETE FROM harvesters.monitored_for "
                    "WHERE path_id=(%s)"
                ),
                [self.monitor_path_id],
            )
            self._insert_monitored_paths(cursor)

    def delete(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "DELETE FROM harvesters.monitored_path "
                    "WHERE monitor_path_id=(%s)"
                ),
                [self.monitor_path_id],
            )

    @staticmethod
    def _get_monitored_for(id_, cursor):
            cursor.execute(
                (
                    "SELECT user_id FROM "
                    "harvesters.monitored_for "
                    "WHERE path_id=(%s)"
                ),
                [id_],
            )
            records = cursor.fetchall()
            return [result[0] for result in records]



    @staticmethod
    def select_from_id(id_, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT harvester_id, path FROM "
                    "harvesters.monitored_path "
                    "WHERE monitor_path_id=(%s)"
                ),
                [id_],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return MonitoredPathRow(
                    harvester_id=result[0],
                    monitored_for=(
                        MonitoredPathRow._get_monitored_for(result[0], cursor),
                    ),
                    path=result[1],
                    monitor_path_id=id_,
                )

    @staticmethod
    def select_from_harvester_id(harvester_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT path, monitor_path_id FROM "
                    "harvesters.monitored_path "
                    "WHERE harvester_id=(%s)"
                ),
                [harvester_id],
            )
            records = cursor.fetchall()
            return [
                MonitoredPathRow(
                    harvester_id=harvester_id,
                    monitored_for=(
                        MonitoredPathRow._get_monitored_for(result[1], cursor),
                    ),
                    path=result[0],
                    monitor_path_id=result[1],
                )
                for result in records
            ]

    @staticmethod
    def select_from_harvester_id_and_path(harvester_id, path, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT monitor_path_id FROM "
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
                    monitored_for=(
                        MonitoredPathRow._get_monitored_for(result[0], cursor),
                    ),
                    path=path,
                    monitor_path_id=result[0],
                )

