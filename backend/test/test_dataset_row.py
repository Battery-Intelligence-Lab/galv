from galvanalyser_test_case import GalvanalyserTestCase
from galvanalyser.database.experiment import (
    MetadataRow,
    AccessRow,
    DatasetRow,
    Dataset,
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
