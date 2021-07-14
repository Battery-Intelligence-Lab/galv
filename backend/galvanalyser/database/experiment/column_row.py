import psycopg2
from galvanalyser.database import Row


class ColumnRow(Row):
    def __init__(self, type_id, name, dataset_id, id_=None):
        self.id = id_
        self.type_id = type_id
        self.dataset_id = dataset_id
        self.name = name

    def to_dict(self):
        obj = {
            'id': self.id,
            'name': self.name,
            'type_id': self.type_id,
            'dataset_id': self.dataset_id,
        }
        return obj

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    'INSERT INTO experiment."column" (type_id, name, dataset_id) '
                    "VALUES (%s, %s, %s) RETURNING id"
                ),
                [self.type_id, self.name, self.dataset_id],
            )
            self.id = cursor.fetchone()[0]

    @staticmethod
    def select_from_id(id_, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    'SELECT type_id, dataset_id, name FROM experiment."column" '
                    "WHERE id=(%s)"
                ),
                [id_],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return ColumnRow(
                id_=id_,
                type_id=result[0],
                dataset_id=result[1],
                name=result[2]
            )

    @staticmethod
    def select_from_dataset_with_name(dataset_id, name, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    'SELECT id, type_id FROM experiment."column" '
                    "WHERE dataset_id=(%s) AND name=(%s)"
                ),
                [dataset_id, name],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return ColumnRow(
                id_=result[0],
                type_id=result[1],
                dataset_id=dataset_id,
                name=name,
            )


    @staticmethod
    def select_from_type_id(type_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    'SELECT id, name, dataset_id FROM experiment."column" '
                    "WHERE type_id=(%s)"
                ),
                [type_id],
            )
            records = cursor.fetchall()
            return [
                ColumnRow(
                    id_=result[0],
                    type_id=type_id,
                    name=result[1],
                    dataset_id=result[2],
                )
                for result in records
            ]
