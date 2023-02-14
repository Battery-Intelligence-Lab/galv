import psycopg2
from galvanalyser.database import Row

class ManufacturerRow(Row):
    def __init__(
        self,
        name,
        id=None,
    ):
        self.id = id
        self.name = name


    def to_dict(self):
        obj = {
            'id': self.id,
            'name': self.name,
        }
        return obj

    def __eq__(self, other):
        if isinstance(other, ManufacturerRow):
            return (
                self.id == other.id and
                self.name == other.name
            )

        return False

    def __repr__(self):
        return ('ManufacturerRow({}, {})'
                .format(
                    self.id,
                    self.name,
                ))

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO cell_data.manufacturer (name) "
                    "VALUES (%s)"
                    "RETURNING id"
                ),
                [
                    self.name,
                ],
            )
            self.id = cursor.fetchone()[0]

    def update(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "UPDATE cell_data.manufacturer SET "
                    "name = (%s) "
                    "WHERE id=(%s)"
                ),
                [
                    self.name, self.id
                ],
            )

    def delete(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "DELETE FROM cell_data.manufacturer "
                    "WHERE id=(%s)"
                ),
                [self.id],
            )

    @staticmethod
    def all(conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, name FROM "
                    "cell_data.manufacturer"
                ),
            )
            records = cursor.fetchall()
            return [
                ManufacturerRow(
                    id=result[0],
                    name=result[1],
                )
                for result in records
            ]

    @staticmethod
    def select_from_id(_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT name FROM "
                    "cell_data.manufacturer "
                    "WHERE id=(%s)"
                ),
                [_id],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return ManufacturerRow(
                id=_id,
                name=result[0],
            )
