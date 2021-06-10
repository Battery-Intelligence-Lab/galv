import psycopg2
import pygalvanalyser

class HarvesterRow(pygalvanalyser.Row):
    def __init__(self, machine_id,
                 harvester_name=None,
                 last_successful_run=None,
                 periodic_hour=None, id_=None):
        self.machine_id = machine_id
        self.id = id_
        self.harvester_name = harvester_name
        self.periodic_hour = periodic_hour
        self.last_successful_run = last_successful_run

    def to_dict(self):
        if self.last_successful_run is not None:
            last_successful_run = self.last_successful_run.isoformat()
        else:
            last_successful_run = None
        obj = {
            'id': self.id,
            'machine_id': self.machine_id,
            'periodic_hour': self.periodic_hour,
            'harvester_name': self.harvester_name,
            'last_successful_run': last_successful_run,
        }
        return obj

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO harvesters.harvester "
                "(machine_id, harvester_name, "
                "periodic_hour, last_successful_run) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                [self.machine_id, self.harvester_name,
                 self.periodic_hour,
                 self.last_successful_run],
            )
            self.id = cursor.fetchone()[0]

    def update(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "UPDATE harvesters.harvester SET "
                    "machine_id = (%s), periodic_hour = (%s), "
                    "last_successful_run = (%s), "
                    "harvester_name = (%s) "
                    "WHERE id=(%s)"
                ),
                [self.machine_id, self.periodic_hour,
                 self.last_successful_run, self.harvester_name,
                 self.id],
            )


    def delete(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "DELETE FROM harvesters.harvester "
                    "WHERE id=(%s)"
                ),
                [self.id],
            )

    @staticmethod
    def select_from_id(id_, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT machine_id, periodic_hour, "
                    "last_successful_run, harvester_name "
                    "FROM harvesters.harvester WHERE "
                    "id=(%s)"
                ),
                [id_],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return HarvesterRow(
                id_=id_,
                machine_id=result[0],
                periodic_hour=result[1],
                last_successful_run=result[2],
                harvester_name=result[3],
            )

    @staticmethod
    def select_from_machine_id(machine_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, periodic_hour, last_successful_run, "
                    "harvester_name "
                    "FROM harvesters.harvester WHERE "
                    "machine_id=(%s)"
                ),
                [machine_id],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return HarvesterRow(
                id_=result[0],
                machine_id=machine_id,
                periodic_hour=result[1],
                last_successful_run=result[2],
                harvester_name=result[3],
            )

    @staticmethod
    def all(conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, machine_id, "
                    "periodic_hour, last_successful_run, "
                    "harvester_name "
                    "FROM harvesters.harvester"
                ),
            )
            records = cursor.fetchall()
            return [
                HarvesterRow(
                    machine_id=result[1],
                    periodic_hour=result[2],
                    last_successful_run=result[3],
                    harvester_name=result[4],
                    id_=result[0],
                )
                for result in records
            ]
