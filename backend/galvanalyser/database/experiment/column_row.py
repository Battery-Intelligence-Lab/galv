import psycopg2
from galvanalyser.database import Row


class ColumnRow(Row):
    def __init__(self, type_id, name, id_=None):
        self.id = id_
        self.type_id = type_id
        self.name = name

    def to_dict(self):
        obj = {
            'id': self.id,
            'name': self.name,
            'type_id': self.type_id,
        }
        return obj

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    'INSERT INTO experiment."column" (type_id, name) '
                    "VALUES (%s, %s) RETURNING id"
                ),
                [self.type_id, self.name],
            )
            self.id = cursor.fetchone()[0]

    @staticmethod
    def select_from_id(id_, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    'SELECT type_id, name FROM experiment."column" '
                    "WHERE id=(%s)"
                ),
                [id_],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return ColumnRow(id_=id_, type_id=result[0], name=result[1])

    @staticmethod
    def select_unknown_with_name(name, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    'SELECT id FROM experiment."column" '
                    "WHERE type_id=(-1) AND name=(%s)"
                ),
                [name],
            )
            records = cursor.fetchall()
            return [
                ColumnRow(id_=result[0], type_id=-1, name=name)
                for result in records
            ]

    @staticmethod
    def select_one_unknown_with_name(name, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    'SELECT id FROM experiment."column" '
                    "WHERE type_id=(-1) AND name=(%s)"
                ),
                [name],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return ColumnRow(id_=result[0], type_id=-1, name=name)

    @staticmethod
    def select_from_type_id(type_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    'SELECT id, name FROM experiment."column" '
                    "WHERE type_id=(%s)"
                ),
                [type_id],
            )
            records = cursor.fetchall()
            return [
                ColumnRow(id=result[0], type_id=type_id, name=result[1])
                for result in records
            ]
