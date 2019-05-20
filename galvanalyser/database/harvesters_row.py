import psycopg2


class HarvestersRow:
    def __init__(self, machine_id, id_no=None):
        self.machine_id = machine_id
        self.id_no = id_no

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO harvesters.harvesters (machine_id) VALUES (%s)",
                [self.machine_id],
            )

    @staticmethod
    def select_from_machine_id(machine_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id_no FROM harvesters.harvesters WHERE "
                    "machine_id=(%s)"
                ),
                [machine_id],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return HarvestersRow(id_no=result[0], machine_id=machine_id)
