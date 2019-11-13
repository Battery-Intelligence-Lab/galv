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


class MiscFileDataRow:
    def __init__(
        self,
        dataset_id,
        lower_sample_range,
        upper_sample_range,
        key,
        json_data=None,
        binary_data=None,
    ):
        self.dataset_id = dataset_id
        self.lower_sample_range = lower_sample_range
        self.upper_sample_range = upper_sample_range
        self.key = key
        self.json_data = json_data
        self.binary_data = binary_data

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.misc_file_data (dataset_id, "
                    "sample_range, key, json_data, binary_data) "
                    "VALUES (%s, '[%s, %s)', %s, %s, %s)"
                ),
                [
                    self.dataset_id,
                    self.lower_sample_range,
                    self.upper_sample_range,
                    self.key,
                    json.dumps(self.json_data, default=json_serial),
                    self.binary_data,
                ],
            )

    @staticmethod
    def select_from_dataset_id(dataset_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT sample_range, key, json_data, binary_data FROM "
                    "experiment.misc_file_data "
                    "WHERE dataset_id=(%s)"
                ),
                [dataset_id],
            )
            records = cursor.fetchall()
            return [
                MiscFileDataRow(
                    dataset_id=dataset_id,
                    lower_sample_range=result[0].lower,
                    upper_sample_range=result[0].upper,
                    key=result[1],
                    json_data=json.loads(result[2])
                    if result[2] is not None
                    else None,
                    binary_data=bytes(result[3])
                    if result[3] is not None
                    else None,
                )
                for result in records
            ]
