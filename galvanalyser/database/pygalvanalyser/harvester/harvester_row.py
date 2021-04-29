import psycopg2


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
