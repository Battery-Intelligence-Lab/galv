from galvanalyser_test_case import GalvanalyserTestCase
from pygalvanalyser.experiment.metadata_row import MetadataRow
from pygalvanalyser.experiment.dataset_row import DatasetRow
import datetime

class TestDatasetRow(GalvanalyserTestCase):
    def test_insert(self):
        dataset = DatasetRow(
            name='dummy',
            date=datetime.datetime.now(),
            institution_id=self.oxford.id,
            dataset_type='test',
            original_collector='test',
        )
        dataset.insert(self.harvester_conn)

        dataset2 = DatasetRow.select_from_id(
            dataset.id, self.user_conn
        )

        self.assertEqual(dataset, dataset2)
