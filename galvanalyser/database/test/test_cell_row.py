from galvanalyser_test_case import GalvanalyserTestCase
from pygalvanalyser.cell_data.cell_row import CellRow
from pygalvanalyser.cell_data.manufacturer_row import ManufacturerRow

class TestCellRow(GalvanalyserTestCase):
    def setUp(self):
        self.manufacturer = ManufacturerRow(
            name='test_cell_row',
        )
        self.manufacturer.insert(self.postgres_conn)
        self.postgres_conn.commit()

    def test_insert_and_select(self):
        uid = '123e4567-e89b-12d3-a456-426614174000'
        cell = CellRow(
            uid=uid,
            manufacturer_id=self.manufacturer.id,
        )
        cell.insert(self.postgres_conn)
        self.postgres_conn.commit()

        cell2 = CellRow.select_from_uid(
            uid,
            self.user_conn
        )
        self.assertEqual(cell, cell2)
