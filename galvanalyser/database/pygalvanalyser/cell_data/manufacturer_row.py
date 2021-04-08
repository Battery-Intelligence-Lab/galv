import psycopg2

class ManufacturerRow:
    def __init__(
        self,
        name,
        id=None,
    ):
        self.id = id
        self.name = name

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
