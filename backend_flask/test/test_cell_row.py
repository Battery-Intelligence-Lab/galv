from test_case import GalvanalyserTestCase
from galvanalyser.database.cell_data import (
    Cell,
)

from sqlalchemy import select

class TestCellRow(GalvanalyserTestCase):
    def test_insert(self):
        with self.Session() as session:
            uid = '123e4567-e89b-12d3-a456-426614174000'
            cell = Cell(
                name=uid,
            )
            session.add(cell)
            session.commit()
            cell2 = session.execute(
                select(Cell).where(Cell.id == cell.id)
            ).one()[0]

            self.assertEqual(cell, cell2)
            self.assertEqual(cell, cell2)
