from galvanalyser_test_case import GalvanalyserTestCase
from pygalvanalyser.cell_data.manufacturer_row import ManufacturerRow

class TestManuacturerRow(GalvanalyserTestCase):
    def test_insert(self):
        manufacturer = ManufacturerRow(
            name='test_manufacturer_row',
        )
        manufacturer.insert(self.postgres_conn)

        self.postgres_conn.commit()

        manufacturer2 = ManufacturerRow.select_from_id(
            manufacturer.id, self.user_conn
        )

        self.assertEqual(manufacturer, manufacturer2)
