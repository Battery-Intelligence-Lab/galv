import psycopg2
import pygalvanalyser
from pygalvanalyser.harvester import MonitoredPathRow

class ObservedFileRow(pygalvanalyser.Row):
    def __init__(
        self,
        monitor_path_id,
        path,
        last_observed_size,
        last_observed_time,
        file_state=None,
    ):
        self.monitor_path_id = monitor_path_id
        self.path = path
        self.last_observed_size = last_observed_size
        self.last_observed_time = last_observed_time
        self.file_state = file_state

    def to_dict(self):
        obj = {
            'monitor_path_id': self.monitor_path_id,
            'path': self.path,
            'last_observed_size': self.last_observed_size,
            'last_observed_time': self.last_observed_time.isoformat(),
            'file_state': self.file_state,
        }
        return obj

    def __str__(self):
        return (
            'ObservedFileRow(monitor_path_id={}, path={} '
            'last_observed_size={}, last_observed_time={} '
            'file_state={})'
        ).format(
            self.monitor_path_id,
            self.path,
            self.last_observed_size,
            self.last_observed_time,
            self.file_state
        )

    def insert(self, conn):
        with conn.cursor() as cursor:
            if self.file_state is None:
                cursor.execute(
                    (
                        "INSERT INTO harvesters.observed_file "
                        "(monitor_path_id, path, last_observed_size, "
                        "last_observed_time) VALUES (%s, %s, %s, %s) "
                        "ON CONFLICT ON CONSTRAINT observed_file_pkey "
                        "DO UPDATE SET "
                        "last_observed_size = %s, last_observed_time = %s"
                    ),
                    [
                        self.monitor_path_id,
                        self.path,
                        self.last_observed_size,
                        self.last_observed_time,
                        self.last_observed_size,
                        self.last_observed_time,
                    ],
                )
            else:
                cursor.execute(
                    (
                        "INSERT INTO harvesters.observed_file "
                        "(monitor_path_id, path, last_observed_size, "
                        "last_observed_time, file_state) "
                        "VALUES (%s, %s, %s, %s, %s) "
                        "ON CONFLICT ON CONSTRAINT observed_file_pkey "
                        "DO UPDATE SET "
                        "last_observed_size = %s, last_observed_time = %s, "
                        "file_state = %s"
                    ),
                    [
                        self.monitor_path_id,
                        self.path,
                        self.last_observed_size,
                        self.last_observed_time,
                        self.file_state,
                        self.last_observed_size,
                        self.last_observed_time,
                        self.file_state,
                    ],
                )

    @staticmethod
    def select_from_id_and_path(monitor_path_id, path, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT last_observed_size, last_observed_time, "
                    "file_state FROM "
                    "harvesters.observed_file WHERE "
                    "monitor_path_id=(%s) AND path=(%s)"
                ),
                [monitor_path_id, path],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return ObservedFileRow(
                monitor_path_id,
                path,
                last_observed_size=result[0],
                last_observed_time=result[1],
                file_state=result[2],
            )

    @staticmethod
    def select_from_id_(monitor_path_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT path, last_observed_size, last_observed_time, "
                    "file_state FROM "
                    "harvesters.observed_file WHERE monitor_path_id=(%s)"
                ),
                [monitor_path_id],
            )
            records = cursor.fetchall()
            return [
                ObservedFileRow(
                    monitor_path_id,
                    path=result[0],
                    last_observed_size=result[1],
                    last_observed_time=result[2],
                    file_state=result[3],
                )
                for result in records
            ]

    @staticmethod
    def select_from_harvester_id_with_state(harvester_id, file_state, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT hof.monitor_path_id, hof.path, "
                    "hof.last_observed_size, hof.last_observed_time "
                    "FROM harvesters.observed_file AS hof "
                    "INNER JOIN harvesters.monitored_path AS hmp ON "
                    "hof.monitor_path_id = hmp.monitor_path_id "
                    "WHERE "
                    "hmp.harvester_id=(%s) AND hof.file_state=(%s)"
                ),
                [harvester_id, file_state],
            )
            records = cursor.fetchall()
            return [
                ObservedFileRow(
                    monitor_path_id=result[0],
                    path=result[1],
                    last_observed_size=result[2],
                    last_observed_time=result[3],
                    file_state=file_state,
                )
                for result in records
            ]


class ObservedFilePathRow:
    def __init__(
        self,
        monitor_path_id,
        monitored_path,
        observed_path,
        monitored_for,
        last_observed_size,
        last_observed_time,
        file_state=None,
    ):
        self.monitor_path_id = monitor_path_id
        self.monitored_path = monitored_path
        self.observed_path = observed_path
        self.monitored_for = monitored_for
        self.last_observed_size = last_observed_size
        self.last_observed_time = last_observed_time
        self.file_state = file_state



    @staticmethod
    def select_from_harvester_id_with_state(harvester_id, file_state, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT hof.monitor_path_id, hmp.path, hof.path, "
                    "hof.last_observed_size, "
                    "hof.last_observed_time "
                    "FROM harvesters.observed_file AS hof "
                    "INNER JOIN harvesters.monitored_path AS hmp ON "
                    "hof.monitor_path_id = hmp.monitor_path_id "
                    "WHERE "
                    "hmp.harvester_id=(%s) AND hof.file_state=(%s)"
                ),
                [harvester_id, file_state],
            )
            records = cursor.fetchall()
            return [
                ObservedFilePathRow(
                    monitor_path_id=result[0],
                    monitored_path=result[1],
                    observed_path=result[2],
                    monitored_for=(
                        MonitoredPathRow._get_monitored_for(result[0], cursor)
                    ),
                    last_observed_size=result[3],
                    last_observed_time=result[4],
                    file_state=file_state,
                )
                for result in records
            ]

    def update_observed_file_state(self, file_state, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "UPDATE harvesters.observed_file SET file_state = %s"
                    "WHERE monitor_path_id=(%s) AND path=(%s)"
                ),
                [file_state, self.monitor_path_id, self.observed_path],
            )

    def update_observed_file_state_if_state_is(
        self, new_file_state, current_file_state, conn
    ):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "UPDATE harvesters.observed_file SET file_state = %s"
                    "WHERE monitor_path_id=(%s) AND path=(%s) "
                    "AND file_state=(%s)"
                ),
                [
                    new_file_state,
                    self.monitor_path_id,
                    self.observed_path,
                    current_file_state,
                ],
            )
            return cursor.rowcount
