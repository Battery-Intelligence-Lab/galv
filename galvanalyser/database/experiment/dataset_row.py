import psycopg2


class DatasetRow:
    def __init__(
        self,
        name,
        date,
        institution_id,
        dataset_type,
        original_collector,
        id_=None,
    ):
        self.id = id_
        self.name = name
        self.date = date
        self.institution_id = institution_id
        self.dataset_type = dataset_type
        self.original_collector = original_collector

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.dataset (name, date, "
                    "institution_id, type, original_collector) "
                    "VALUES (%s, %s, %s, %s, %s) "
                    "RETURNING id"
                ),
                [
                    self.name,
                    self.date,
                    self.institution_id,
                    self.dataset_type,
                    self.original_collector,
                ],
            )
            self.id = cursor.fetchone()[0]
            # except
            # psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "dataset_pkey"
            # DETAIL:  Key (name, date)=(TPG1+-+Cell+15+-+002, 2018-02-23 08:42:16+00) already exists.

    @staticmethod
    def select_from_name_date_and_institution_id(
        name, date, institution_id, conn
    ):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, type, original_collector FROM experiment.dataset "
                    "WHERE name=(%s) AND date=(%s) AND institution_id=(%s)"
                ),
                [name, date, institution_id],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return DatasetRow(
                id_=result[0],
                name=name,
                date=date,
                institution_id=institution_id,
                dataset_type=result[1],
                original_collector=result[2],
            )

    @staticmethod
    def select_from_id(id_, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT name, date, institution_id, type, original_collector "
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
                institution_id=result[2],
                dataset_type=result[3],
                original_collector=result[4],
            )

    @staticmethod
    def select_all_dataset(conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, name, date, institution_id, type, "
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
                    institution_id=result[3],
                    dataset_type=result[4],
                    original_collector=result[5],
                )
                for result in records
            ]

    @staticmethod
    def select_filtered_dataset(
        conn, name_like, min_date, max_date, dataset_type
    ):
        with conn.cursor() as cursor:
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

            cursor.execute(
                (
                    "SELECT id, name, date, institution_id, type, "
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
                    institution_id=result[3],
                    dataset_type=result[4],
                    original_collector=result[5],
                )
                for result in records
            ]
