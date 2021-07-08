from galvanalyser_test_case import GalvanalyserTestCase
from galvanalyser.database.experiment import (
    MetadataRow,
    AccessRow,
    DatasetRow,
    Dataset,
    Equipment,
    Column,
    TimeseriesData,
)
from galvanalyser.database.cell_data import (
    Cell
)
from sqlalchemy import select
import datetime

class TestDatasetRow(GalvanalyserTestCase):
    def test_insert(self):
        with self.HarvesterSession() as session:
            dataset = Dataset(
                name='test_dataset_row',
                date=datetime.datetime.now(),
                type='test',
            )
            session.add(dataset)
            session.commit()
            dataset2 = session.execute(
                select(Dataset).where(Dataset.id == dataset.id)
            ).one()[0]

            self.assertEqual(dataset, dataset2)

    def test_dataset_relationships(self):
        with self.Session() as session:
            # create dataset
            dataset = Dataset(
                name='tester',
                date=datetime.datetime.now(),
                type='test',
            )
            session.add(dataset)
            session.commit()

            # add equipment
            equip = Equipment(
                name='test', type='test type'
            )
            session.add(equip)
            dataset.equipment = [equip]

            # add cell
            cell = Cell(
                name='test'
            )
            session.add(cell)
            dataset.cell = cell

            # add samples
            column0 = session.get(Column, 0)
            column1 = session.get(Column, 1)
            session.bulk_save_objects([
                TimeseriesData(
                    dataset_id=dataset.id,
                    sample_no=0,
                    column_id=column0.id,
                    value=0
                ),
                TimeseriesData(
                    dataset_id=dataset.id,
                    sample_no=1,
                    column_id=column0.id,
                    value=1
                ),
                TimeseriesData(
                    dataset_id=dataset.id,
                    sample_no=2,
                    column_id=column0.id,
                    value=2
                ),
                TimeseriesData(
                    dataset_id=dataset.id,
                    sample_no=0,
                    column_id=column1.id,
                    value=0
                ),

            ])
            session.commit()
            self.assertEqual(len(dataset.columns), 2)
            self.assertEqual(len(dataset.equipment), 1)




