import psycopg2
import json


class HarvesterRow:
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

    @classmethod
    def to_json(cls, arg):
        if isinstance(arg, list):
            list_obj = [x.to_dict() for x in arg]
            return json.dumps(list_obj)
        elif isinstance(arg, cls):
            return json.dumps(arg.to_dict())

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
