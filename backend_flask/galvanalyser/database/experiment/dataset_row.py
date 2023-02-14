import psycopg2
from galvanalyser.database import Row
from galvanalyser.database.experiment import (
    EquipmentRow,
    ColumnRow,
    RangeLabelRow,
)
from galvanalyser.database.cell_data import (
    CellRow,
)
from galvanalyser.database.user_data import (
    UserRow
)

from datetime import date, datetime
import json


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code
    Modified from https://stackoverflow.com/a/22238613
    """

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


class DatasetRow(Row):
    def __init__(
        self,
        name,
        date,
        dataset_type,
        id_=None,
        cell_id=None,
        owner_id=None,
        purpose=None,
        equipment=None,
        json_data=None
    ):
        self.id = id_
        self.name = name
        self.date = date
        self.dataset_type = dataset_type
        self.cell_id = cell_id
        self.owner_id = owner_id
        self.purpose = purpose
        if equipment is None:
            self.equipment = []
        else:
            self.equipment = equipment
        self.json_data = json_data

    def __eq__(self, other):
        return self.id == other.id

    def to_dict(self, conn):
        json_str = json.dumps(self.json_data, default=json_serial)
        cell = CellRow.select_from_id(self.cell_id, conn)
        equipment = [
            EquipmentRow.select_from_id(id_, conn) for id_ in self.equipment
        ]
        ranges = RangeLabelRow.select_from_dataset_id(self.id, conn)
        owner = UserRow.select_from_id(self.owner_id, conn)
        obj = {
            'id': self.id,
            'name': self.name,
            'date': self.date.isoformat(),
            'dataset_type': self.dataset_type,
            'cell': CellRow.to_dict(cell),
            'owner': UserRow.to_dict(owner),
            'purpose': self.purpose,
            'ranges': [RangeLabelRow.to_dict(r) for r in ranges],
            'equipment': [EquipmentRow.to_dict(e) for e in equipment],
            'json_data': json_str,
        }
        return obj

    def __repr__(self):
        return 'DatasetRow({}, {}, {}, {})'.format(
            self.id, self.name, self.date,
            self.dataset_type
        )

    def update(self, conn, update_equipment=True):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "UPDATE experiment.dataset SET "
                    "name = (%s), "
                    "cell_id = (%s), owner_id = (%s), "
                    "purpose = (%s) "
                    "WHERE id=(%s)"
                ),
                [
                    self.name,
                    self.cell_id, self.owner_id,
                    self.purpose,
                    self.id
                ],
            )
            if update_equipment:
                cursor.execute(
                    (
                        "DELETE FROM experiment.dataset_equipment "
                        "WHERE dataset_id=(%s)"
                    ),
                    [self.id],
                )
                self._insert_equipment(cursor)

    @staticmethod
    def _get_equipment(id_, cursor):
        cursor.execute(
            (
                "SELECT equipment_id FROM "
                "experiment.dataset_equipment"
                "WHERE dataset_id=(%s)"
            ),
            [id_],
        )
        records = cursor.fetchall()
        return [result[0] for result in records]

    def _insert_equipment(self, cursor):
        if len(self.equipment) > 0:
            equipment_rows = b','.join(
                cursor.mogrify(
                    "(%s,%s)", [self.id, x]
                )
                for x in self.equipment
            )
            cursor.execute(
                (
                    b"INSERT INTO experiment.dataset_equipment"
                    b"(dataset_id, equipment_id) VALUES " + equipment_rows
                ),
                [equipment_rows],
            )

    def insert(self, conn):
        # make sure we dont have any null unicode values in the json
        json_str = json.dumps(self.json_data, default=json_serial)
        json_str = json_str.replace(r'\u0000', '')

        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.dataset "
                    "(name, date, type, "
                    "cell_id, owner_id, purpose, "
                    "json_data) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                    "RETURNING id"
                ),
                [
                    self.name,
                    self.date,
                    self.dataset_type,
                    self.cell_id,
                    self.owner_id,
                    self.purpose,
                    json_str,
                ],
            )

            self.id = cursor.fetchone()[0]

            self._insert_equipment(cursor)

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
    def _get_equipment(id_, cursor):
        cursor.execute(
            (
                "SELECT equipment_id FROM "
                "experiment.dataset_equipment "
                "WHERE dataset_id=(%s)"
            ),
            [id_],
        )
        records = cursor.fetchall()
        return [result[0] for result in records]

    @staticmethod
    def select_from_name_date(
        name, date, conn
    ):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT "
                    "id, type, "
                    "cell_id, owner_id, purpose, "
                    "json_data "
                    "FROM experiment.dataset "
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
                cell_id=result[2],
                owner_id=result[3],
                purpose=result[4],
                equipment=(
                    DatasetRow._get_equipment(result[0], cursor)
                ),
                json_data=json.loads(result[5])
                if result[5] is not None
                else None,
            )

    @staticmethod
    def select_from_id(id_, conn, get_equipment=True):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT name, date, type, "
                    "cell_id, owner_id, purpose, "
                    "json_data "
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
                cell_id=result[3],
                owner_id=result[4],
                purpose=result[5],
                equipment=(
                    DatasetRow._get_equipment(id_, cursor) if get_equipment else None
                ),
                json_data=json.loads(result[6])
                if result[6] is not None
                else None,

            )

    @staticmethod
    def all_result(records, cursor):
        return [
            DatasetRow(
                id_=result[0],
                name=result[1],
                date=result[2],
                dataset_type=result[3],
                cell_id=result[4],
                owner_id=result[5],
                purpose=result[6],
                equipment=(
                    DatasetRow._get_equipment(result[0], cursor)
                ),
                json_data=json.loads(result[7])
                if result[7] is not None
                else None,
            )
            for result in records
        ]

    @staticmethod
    def all(conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, name, date, type, "
                    "cell_id, owner_id, purpose, "
                    "json_data "
                    "FROM experiment.dataset"
                )
            )
            records = cursor.fetchall()
            return DatasetRow.all_result(records, cursor)

    @staticmethod
    def all_with_access(user_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, name, date, type, "
                    "cell_id, owner_id, purpose, "
                    "json_data "
                    "FROM experiment.dataset "
                    "LEFT JOIN experiment.access ON "
                    "experiment.access.dataset_id = id "
                    "WHERE experiment.access.user_id=(%s)"
                ),
                [user_id]
            )
            records = cursor.fetchall()
            return DatasetRow.all_result(records, cursor)

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
            return DatasetRow.all(conn)
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, name, date, type, "
                    "cell_id, owner_id, purpose, "
                    "json_data "
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
                    cell_id=result[4],
                    owner_id=result[5],
                    purpose=result[6],
                    equipment=(
                        DatasetRow._get_equipment(result[0], cursor)
                    ),
                    json_data=json.loads(result[7])
                    if result[7] is not None
                    else None,
                )
                for result in records
            ]
