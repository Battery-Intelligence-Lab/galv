from galvanalyser_test_case import GalvanalyserTestCase
from pygalvanalyser.experiment.metadata_row import MetadataRow
from pygalvanalyser.experiment.dataset_row import DatasetRow
import datetime

class TestMetadataRow(GalvanalyserTestCase):
    def setUp(self):
        self.dataset = DatasetRow(
            name='test_metadata_row',
            date=datetime.datetime.now(),
            institution_id=self.oxford.id,
            dataset_type='test',
            original_collector='test',
        )
        self.dataset.insert(self.postgres_conn)
        self.postgres_conn.commit()

    def test_insert_and_select(self):
        metadata = MetadataRow(
            dataset_id=self.dataset.id,
        )
        metadata.insert(self.postgres_conn)
        self.postgres_conn.commit()

        metadata2 = MetadataRow.select_from_dataset_id(
            self.dataset.id,
            self.user_conn
        )
        self.assertEqual(metadata, metadata2)
