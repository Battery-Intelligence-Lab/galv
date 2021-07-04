from galvanalyser_test_case import GalvanalyserTestCase
from galvanalyser.database import db
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
        dataset = Dataset(
            name='test_dataset_row',
            date=datetime.datetime.now(),
            dataset_type='test',
        )
        db.session.add(dataset, bind='harvester')
        db.session.commit()
        result = session.execute(
            select(Dataset).where(Dataset.id == dataset.id)
        )

        self.assertEqual(dataset, result.first())
