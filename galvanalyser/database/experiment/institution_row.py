import psycopg2


class InstitutionRow:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.institution (id, name) "
                    "VALUES (%s, %s) ON CONFLICT DO NOTHING"
                ),
                [self.id, self.name],
            )

    @staticmethod
    def select_from_id(id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT name FROM experiment.institution "
                    "WHERE id=(%s)"
                ),
                [id],
            )
            records = cursor.fetchall()
            return [
                InstitutionRow(id=id, name=result[0])
                for result in records
            ]

    @staticmethod
    def select_from_name(name, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id FROM experiment.institution "
                    "WHERE name=(%s)"
                ),
                [name],
            )
            records = cursor.fetchall()
            return [
                InstitutionRow(id=result[0], name=name)
                for result in records
            ]
