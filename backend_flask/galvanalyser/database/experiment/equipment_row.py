import psycopg2
from galvanalyser.database import Row


class EquipmentRow(Row):
    def __init__(
        self,
        name,
        id=None,
        type=None,
    ):
        self.id = id
        self.name = name
        self.type = type

    def to_dict(self):
        obj = {
            'id': self.id,
            'name': self.name,
            'type': self.type,
        }
        return obj

    def __eq__(self, other):
        if isinstance(other, EquipmentRow):
            return (
                self.id == other.id and
                self.name == other.name and
                self.type == other.type
            )

        return False

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.equipment ("
                    "name, type) "
                    "VALUES (%s, %s) "
                    "RETURNING id"
                ),
                [
                    self.name,
                    self.type,
                ],
            )
            result = cursor.fetchone()
            self.id = result[0]

    def update(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "UPDATE experiment.equipment SET "
                    "name = (%s), "
                    "type = (%s) "
                    "WHERE id=(%s)"
                ),
                [
                    self.name,
                    self.type, self.id,
                ],
            )

    def delete(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "DELETE FROM experiment.equipment "
                    "WHERE id=(%s)"
                ),
                [self.id],
            )

    @staticmethod
    def all(conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, name, type "
                    "FROM "
                    "experiment.equipment"
                ),
            )
            records = cursor.fetchall()
            return [
                EquipmentRow(
                    id=result[0],
                    name=result[1],
                    type=result[2],
                )
                for result in records
            ]

    @staticmethod
    def select_from_id(id_, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT name, type "
                    "FROM "
                    "experiment.equipment "
                    "WHERE id=(%s)"
                ),
                [id_],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return EquipmentRow(
                id=id_,
                name=result[0],
                type=result[1],
            )

    @staticmethod
    def select_from_name(name, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, type "
                    "FROM "
                    "experiment.equipment "
                    "WHERE name=(%s)"
                ),
                [name],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return EquipmentRow(
                id=result[0],
                name=name,
                type=result[1],
            )
