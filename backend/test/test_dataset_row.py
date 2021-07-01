from galvanalyser_test_case import GalvanalyserTestCase
from pygalvanalyser.experiment.metadata_row import MetadataRow
from pygalvanalyser.experiment.access_row import AccessRow
from pygalvanalyser.experiment.dataset_row import DatasetRow
import datetime

class TestDatasetRow(GalvanalyserTestCase):
    def test_insert(self):
        dataset = DatasetRow(
            name='test_dataset_row',
            date=datetime.datetime.now(),
            institution_id=self.oxford.id,
            dataset_type='test',
            original_collector='test',
        )
        dataset.insert(self.harvester_conn)

        self.harvester_conn.commit()

        dataset2 = DatasetRow.select_from_id(
            dataset.id, self.harvester_conn
        )

        self.assertEqual(dataset, dataset2)

        # no access for this user currently
        self.assertIsNone(DatasetRow.select_from_id(
            dataset.id, self.user_conn
        ))

        access = AccessRow(dataset.id, self.USER)
        access.insert(self.harvester_conn)

        self.harvester_conn.commit()

        # now we'll get the row since the user has access
        dataset2 = DatasetRow.select_from_id(
            dataset.id, self.user_conn
        )

        self.assertEqual(dataset, dataset2)
