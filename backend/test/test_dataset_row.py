from test_case import GalvanalyserTestCase
from galvanalyser.database.experiment import (
    MetadataRow,
    AccessRow,
    DatasetRow,
    Dataset,
    Equipment,
    Column,
    TimeseriesData,
    RangeLabel,
    ColumnType,
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
            column_type = session.get(ColumnType, -1)
            column0 = Column(
                name='test',
                dataset_id=dataset.id,
                type_id=column_type.id,
            )
            session.add(column0)
            column1 = Column(
                name='test2',
                dataset_id=dataset.id,
                type_id=column_type.id,
            )
            session.add(column1)
            session.commit()

            session.bulk_save_objects([
                TimeseriesData(
                    sample_no=0,
                    column_id=column0.id,
                    value=0
                ),
                TimeseriesData(
                    sample_no=1,
                    column_id=column0.id,
                    value=1
                ),
                TimeseriesData(
                    sample_no=2,
                    column_id=column0.id,
                    value=2
                ),
                TimeseriesData(
                    sample_no=0,
                    column_id=column1.id,
                    value=0
                ),

            ])

            range_label = RangeLabel(
                label_name='test',
                dataset_id=dataset.id,
                sample_range=[0, 2],
                info="a description here"
            )
            session.add(range_label)
            session.commit()
            self.assertEqual(len(dataset.columns), 2)
            self.assertEqual(len(dataset.equipment), 1)
            self.assertEqual(len(dataset.ranges), 1)
