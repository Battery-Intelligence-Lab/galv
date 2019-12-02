import psycopg2


class RangeLabelRow:
    def __init__(
        self,
        dataset_id,
        label_name,
        created_by,
        lower_bound,
        upper_bound,
        info=None,
        user_created=False,
        id_=None,
    ):
        self.id = id_
        self.dataset_id = dataset_id
        self.label_name = label_name
        self.created_by = created_by
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.info = info
        self.user_created = user_created

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO experiment.range_label "
                    "(dataset_id, label_name, created_by, sample_range, info) "
                    "VALUES (%s, %s, %s, '[%s, %s)', %s) "
                    "ON CONFLICT ON CONSTRAINT range_label_pkey DO UPDATE SET "
                    "sample_range = '[%s, %s)', info = %s "
                    "RETURNING id"
                ),
                [
                    self.dataset_id,
                    self.label_name,
                    self.created_by,
                    self.lower_bound,
                    self.upper_bound,
                    self.info,
                    self.lower_bound,
                    self.upper_bound,
                    self.info,
                ],
            )
            self.id = cursor.fetchone()[0]

    @staticmethod
    def select_from_dataset_id(dataset_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, label_name, created_by, sample_range, info, "
                    "tableoid!='experiment.range_label'::regclass::oid as "
                    "user_created "
                    "FROM experiment.range_label "
                    "WHERE dataset_id=(%s)"
                ),
                [dataset_id],
            )
            records = cursor.fetchall()
            return [
                RangeLabelRow(
                    id_=result[0],
                    dataset_id=dataset_id,
                    label_name=result[1],
                    created_by=result[2],
                    lower_bound=result[3].lower,
                    upper_bound=result[3].upper,
                    info=result[4],
                    user_created=result[5],
                )
                for result in records
            ]

    @staticmethod
    def select_from_dataset_id_and_label_name(dataset_id, label_name, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, created_by, sample_range, info, "
                    "tableoid!='experiment.range_label'::regclass::oid as "
                    "user_created "
                    "FROM experiment.range_label "
                    "WHERE dataset_id=(%s) AND label_name=(%s)"
                ),
                [dataset_id, label_name],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return RangeLabelRow(
                id_=result[0],
                dataset_id=dataset_id,
                label_name=label_name,
                created_by=result[1],
                lower_bound=result[2][0],
                upper_bound=result[2][1],
                info=result[3],
                user_created=result[4],
            )

    @staticmethod
    def select_filtered_from_dataset_id(dataset_id, conn, name_like=None, system_made=True, user_made=True):
        filter_query = []
        filter_values = [dataset_id]
        if name_like is not None and len(name_like) > 0:
            filter_query.append("label_name LIKE %s")
            filter_values.append(name_like)
        if not system_made:
            if not user_made:
                return []
            else:
                filter_query.append("user_created = TRUE")
        else:
            if not user_made:
                filter_query.append("user_created = FALSE")
        if len(filter_query) == 0:
            return RangeLabelRow.select_from_dataset_id(dataset_id, conn)
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT * FROM ("
                    "SELECT id, label_name, created_by, sample_range, info, "
                    "tableoid!='experiment.range_label'::regclass::oid as "
                    "user_created "
                    "FROM experiment.range_label "
                    "WHERE dataset_id=(%s)"
                    ") as t WHERE " + (" AND ".join(filter_query))
                ),
                filter_values,
            )
            records = cursor.fetchall()
            return [
                RangeLabelRow(
                    id_=result[0],
                    dataset_id=dataset_id,
                    label_name=result[1],
                    created_by=result[2],
                    lower_bound=result[3].lower,
                    upper_bound=result[3].upper,
                    info=result[4],
                    user_created=result[5],
                )
                for result in records
            ]
