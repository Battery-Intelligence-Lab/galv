import psycopg2
import pygalvanalyser


class InstitutionRow(pygalvanalyser.Row):
    def __init__(self, name, id_=None):
        self.id = id_
        self.name = name

    def to_dict(self):
        obj = {
            'id': self.id,
            'name': self.name,
        }
        return obj

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.institution (name) "
                    "VALUES (%s)"
                ),
                [self.name],
            )

    def update(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "UPDATE experiment.institution SET "
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
                    "DELETE FROM experiment.institution"
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
                    "experiment.institution"
                ),
            )
            records = cursor.fetchall()
            return [
                InstitutionRow(
                    id_=result[0],
                    name=result[1],
                )
                for result in records
            ]

    @staticmethod
    def select_from_id(id_, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                ("SELECT name FROM experiment.institution " "WHERE id=(%s)"),
                [id_],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return InstitutionRow(id_=id_, name=result[0])

    @staticmethod
    def select_from_name(name, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                ("SELECT id FROM experiment.institution " "WHERE name=(%s)"),
                [name],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return InstitutionRow(id_=result[0], name=name)
