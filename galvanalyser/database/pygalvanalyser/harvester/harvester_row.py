import psycopg2
import pygalvanalyser

class HarvesterRow(pygalvanalyser.Row):
    def __init__(self, machine_id, id_=None):
        self.machine_id = machine_id
        self.id = id_

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO harvesters.harvester (machine_id) "
                "VALUES (%s) RETURNING id",
                [self.machine_id],
            )
            self.id = cursor.fetchone()[0]

    def to_dict(self):
        obj = {
            'id': self.id,
            'machine_id': self.machine_id,
        }
        return obj

    @staticmethod
    def select_from_id(id_, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT machine_id FROM harvesters.harvester WHERE "
                    "id=(%s)"
                ),
                [id_],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return HarvesterRow(id_=id_, machine_id=result[0])

    @staticmethod
    def select_from_machine_id(machine_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id FROM harvesters.harvester WHERE "
                    "machine_id=(%s)"
                ),
                [machine_id],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return HarvesterRow(id_=result[0], machine_id=machine_id)

    @staticmethod
    def all(conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, machine_id FROM harvesters.harvester"
                ),
            )
            records = cursor.fetchall()
            return [
                HarvesterRow(
                    machine_id=result[1],
                    id_=result[0],
                )
                for result in records
            ]
