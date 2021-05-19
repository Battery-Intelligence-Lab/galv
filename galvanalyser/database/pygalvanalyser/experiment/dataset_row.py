import psycopg2
import pygalvanalyser
from datetime import date, datetime
import json

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code
    Modified from https://stackoverflow.com/a/22238613
    """

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


class DatasetRow(pygalvanalyser.Row):
    def __init__(
        self,
        name,
        date,
        dataset_type,
        original_collector,
        id_=None,
        cell_id=None,
        owner=None,
        purpose=None,
        test_equipment=None,
        json_data=None
    ):
        self.id = id_
        self.name = name
        self.date = date
        self.dataset_type = dataset_type
        self.original_collector = original_collector
        self.cell_id = cell_id
        self.owner = owner
        self.purpose = purpose
        self.test_equipment = test_equipment
        self.json_data = json_data

    def to_dict(self):
        json_str = json.dumps(self.json_data, default=json_serial)
        obj = {
            'id': self.id,
            'name': self.name,
            'date': self.date.isoformat(),
            'dataset_type': self.dataset_type,
            'original_collector': self.original_collector,
            'cell_id': self.cell_id,
            'owner': self.owner,
            'purpose': self.purpose,
            'test_equipment': self.test_equipment,
            'json_data': json_str,
        }
        return obj

    def __repr__(self):
        return 'DatasetRow({}, {}, {}, {}, {})'.format(
            self.id, self.name, self.date,
            self.dataset_type, self.original_collector
        )

    def __eq__(self, other):
        if isinstance(other, DatasetRow):
            return (
                self.id == other.id and
                self.name == other.name and
                self.dataset_type == other.dataset_type and
                self.original_collector == other.original_collector
            )

    def insert(self, conn):
        # make sure we dont have any null unicode values in the json
        json_str = json.dumps(self.json_data, default=json_serial)
        json_str = json_str.replace(r'\u0000', '')

        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.dataset "
                    "(name, date, type, original_collector, "
                    "cell_id, owner, purpose, test_equipment, "
                    "json_data) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    "RETURNING id"
                ),
                [
                    self.name,
                    self.date,
                    self.dataset_type,
                    self.original_collector,
                    self.cell_id,
                    self.owner,
                    self.purpose,
                    self.test_equipment,
                    json_str,
                ],
            )
            self.id = cursor.fetchone()[0]

    def delete(self, conn):
        if self.id is None:
            return None

        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "DELETE FROM experiment.dataset "
                    "WHERE id = %s "
                ),
                [
                    self.id,
                ],
            )

        self.id = None

    @staticmethod
    def select_from_name_date(
        name, date, conn
    ):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT "
                    "id, type, original_collector FROM experiment.dataset "
                    "WHERE name=(%s) AND date=(%s)"
                ),
                [name, date],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return DatasetRow(
                id_=result[0],
                name=name,
                date=date,
                dataset_type=result[1],
                original_collector=result[2],
            )

    @staticmethod
    def select_from_id(id_, conn, with_metadata=False):
        if with_metadata:
            with conn.cursor() as cursor:
                cursor.execute(
                    (
                        "SELECT "
                        "experiment.dataset.name, "
                        "experiment.dataset.date, "
                        "experiment.dataset.type, "
                        "experiment.dataset.original_collector, "
                        "experiment.metadata.cell_id, "
                        "experiment.metadata.owner, "
                        "experiment.metadata.purpose, "
                        "experiment.metadata.test_equipment, "
                        "experiment.metadata.json_data "
                        "FROM experiment.dataset "
                        "LEFT JOIN experiment.metadata "
                        "ON experiment.dataset.id = "
                        "experiment.metadata.dataset_id "
                        "WHERE experiment.dataset.id=(%s)"
                    ),
                    [id_]
                )
                result = cursor.fetchone()
                if result is None:
                    return None
                return DatasetRow(
                    id_=id_,
                    name=result[0],
                    date=result[1],
                    dataset_type=result[2],
                    original_collector=result[3],
                )
        else:
            with conn.cursor() as cursor:
                cursor.execute(
                    (
                        "SELECT name, date, type, original_collector "
                        "FROM experiment.dataset WHERE id=(%s)"
                    ),
                    [id_],
                )
                result = cursor.fetchone()
                if result is None:
                    return None
                return DatasetRow(
                    id_=id_,
                    name=result[0],
                    date=result[1],
                    dataset_type=result[2],
                    original_collector=result[3],
                )

    @staticmethod
    def all(conn, with_metadata=False):
        if with_metadata:
            with conn.cursor() as cursor:
                cursor.execute(
                    (
                        "SELECT experiment.dataset.id, "
                        "experiment.dataset.name, "
                        "experiment.dataset.date, "
                        "experiment.dataset.type, "
                        "experiment.dataset.original_collector, "
                        "experiment.metadata.cell_id, "
                        "experiment.metadata.owner, "
                        "experiment.metadata.purpose, "
                        "experiment.metadata.test_equipment, "
                        "experiment.metadata.json_data "
                        "FROM experiment.dataset "
                        "LEFT JOIN experiment.metadata "
                        "ON experiment.dataset.id = "
                        "experiment.metadata.dataset_id"
                    )
                )
                records = cursor.fetchall()
                return [
                    DatasetRow(
                        id_=result[0],
                        name=result[1],
                        date=result[2],
                        dataset_type=result[3],
                        original_collector=result[4],
                        metadata=MetadataRow(
                            dataset_id=result[0],
                            cell_id=result[5],
                            owner=result[6],
                            purpose=result[7],
                            test_equipment=result[8],
                            json_data=result[9]
                        )

                    )
                    for result in records
                ]
        else:
            with conn.cursor() as cursor:
                cursor.execute(
                    (
                        "SELECT id, name, date, type, "
                        "original_collector "
                        "FROM experiment.dataset"
                    )
                )
                records = cursor.fetchall()
                return [
                    DatasetRow(
                        id_=result[0],
                        name=result[1],
                        date=result[2],
                        dataset_type=result[3],
                        original_collector=result[4],
                    )
                    for result in records
                ]

    @staticmethod
    def select_filtered_dataset(
        conn, name_like, min_date, max_date, dataset_type
    ):
        filter_query = ""
        filter_values = []
        if name_like is not None and len(name_like) > 0:
            filter_query = "name LIKE %s"
            filter_values.append(name_like)
        if min_date is not None:
            if filter_query != "":
                filter_query = filter_query + " AND "
            filter_query = filter_query + "date >= %s"
            filter_values.append(min_date)
        if max_date is not None:
            if filter_query != "":
                filter_query = filter_query + " AND "
            filter_query = filter_query + "date <= %s"
            filter_values.append(max_date)
        if dataset_type is not None and len(dataset_type) > 0:
            if filter_query != "":
                filter_query = filter_query + " AND "
            filter_query = filter_query + "type IN %s"
            filter_values.append(tuple(dataset_type))
        if filter_query == "":
            return DatasetRow.select_all_dataset(conn)
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, name, date, type, "
                    "original_collector "
                    "FROM experiment.dataset "
                    "WHERE " + filter_query
                ),
                filter_values,
            )
            records = cursor.fetchall()
            return [
                DatasetRow(
                    id_=result[0],
                    name=result[1],
                    date=result[2],
                    dataset_type=result[3],
                    original_collector=result[4],
                )
                for result in records
            ]
