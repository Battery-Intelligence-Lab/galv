from galvanalyser_test_case import GalvanalyserTestCase
from galvanalyser.database.cell_data import (
    CellRow,
)

class TestCellRow(GalvanalyserTestCase):
    def test_insert_and_select(self):
        uid = '123e4567-e89b-12d3-a456-426614174000'
        cell = CellRow(
            name=uid,
        )
        cell.insert(self.postgres_conn)
        self.postgres_conn.commit()

        cell2 = CellRow.select_from_name(
            uid,
            self.postgres_conn
        )
        self.assertEqual(cell, cell2)
