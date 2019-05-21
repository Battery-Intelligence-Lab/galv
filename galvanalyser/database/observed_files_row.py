import psycopg2


class ObservedFilesRow:
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

    def insert(self, conn):
        with conn.cursor() as cursor:
            if self.file_state is None:
                cursor.execute(
                    (
                        "INSERT INTO harvesters.observed_files "
                        "(monitor_path_id, path, last_observed_size, "
                        "last_observed_time) VALUES (%s, %s, %s, %s) "
                        "ON CONFLICT ON CONSTRAINT observed_files_pkey "
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
                        "INSERT INTO harvesters.observed_files "
                        "(monitor_path_id, path, last_observed_size, "
                        "last_observed_time, file_state) "
                        "VALUES (%s, %s, %s, %s, %s) "
                        "ON CONFLICT ON CONSTRAINT observed_files_pkey "
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
                    "harvesters.observed_files WHERE "
                    "monitor_path_id=(%s) AND path=(%s)"
                ),
                [monitor_path_id, path],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return ObservedFilesRow(
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
                    "harvesters.observed_files WHERE monitor_path_id=(%s)"
                ),
                [monitor_path_id],
            )
            records = cursor.fetchall()
            return [
                ObservedFilesRow(
                    monitor_path_id,
                    path=result[0],
                    last_observed_size=result[1],
                    last_observed_time=result[2],
                    file_state=result[3],
                )
                for result in records
            ]

    @staticmethod
    def select_from_id_with_state(monitor_path_id, file_state, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT path, last_observed_size, last_observed_time "
                    "FROM harvesters.observed_files WHERE "
                    "monitor_path_id=(%s) AND file_state=(%s)"
                ),
                [monitor_path_id, file_state],
            )
            records = cursor.fetchall()
            return [
                ObservedFilesRow(
                    monitor_path_id,
                    path=result[0],
                    last_observed_size=result[1],
                    last_observed_time=result[2],
                    file_state=file_state,
                )
                for result in records
            ]
