import psycopg2
import json
from datetime import date, datetime


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code
    Modified from https://stackoverflow.com/a/22238613
    """

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


class MetadataRow:
    def __init__(
        self,
        dataset_id,
        cell_uid=None,
        owner=None,
        purpose=None,
        test_equipment=None,
        json_data=None,
    ):
        self.dataset_id = dataset_id
        self.cell_uid = cell_uid
        self.owner = owner
        self.purpose = purpose
        self.test_equipment = test_equipment
        self.json_data = json_data

    def __eq__(self, other):
        if isinstance(other, MetadataRow):
            return (
                self.dataset_id == other.dataset_id and
                self.cell_uid == other.cell_uid and
                self.owner == other.owner and
                self.purpose == other.purpose and
                self.test_equipment == other.test_equipment and
                self.json_data == other.json_data
            )

        return False

    def __repr__(self):
        return ('MetadataRow({}, {}, {}, {}, {}, {})'
                .format(
                    self.dataset_id,
                    self.cell_uid,
                    self.owner,
                    self.purpose,
                    self.test_equipment,
                    self.json_data,
                ))

    def insert(self, conn):
        # make sure we dont have any null unicode values in the json
        json_str = json.dumps(self.json_data, default=json_serial)
        json_str = json_str.replace(r'\u0000', '')

        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.metadata (dataset_id, "
                    "cell_uid, owner, purpose, test_equipment, "
                    "json_data) "
                    "VALUES (%s, %s, %s, %s, %s, %s)"
                ),
                [
                    self.dataset_id,
                    self.cell_uid,
                    self.owner,
                    self.purpose,
                    self.test_equipment,
                    json_str,
                ],
            )

    @staticmethod
    def select_from_dataset_id(dataset_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT cell_uid, owner, purpose, "
                    "test_equipment, json_data FROM "
                    "experiment.metadata "
                    "WHERE dataset_id=(%s)"
                ),
                [dataset_id],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return MetadataRow(
                dataset_id=dataset_id,
                cell_uid=result[0],
                owner=result[1],
                purpose=result[2],
                test_equipment=result[3],
                json_data=json.loads(result[4])
                if result[4] is not None
                else None,
            )