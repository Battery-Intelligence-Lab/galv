from galvanalyser_test_case import GalvanalyserTestCase
from galvanalyser.database.experiment import (
    MetadataRow,
    AccessRow,
    DatasetRow
)
import datetime

class TestDatasetRow(GalvanalyserTestCase):
    def test_insert(self):
        dataset = DatasetRow(
            name='test_dataset_row',
            date=datetime.datetime.now(),
            dataset_type='test',
        )
        dataset.insert(self.harvester_conn)

        self.harvester_conn.commit()

        dataset2 = DatasetRow.select_from_id(
            dataset.id, self.harvester_conn,
            get_equipment=False,

        )

        self.assertEqual(dataset, dataset2)
