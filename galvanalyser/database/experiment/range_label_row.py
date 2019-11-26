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
        id_=None,
    ):
        self.id = id_
        self.dataset_id = dataset_id
        self.label_name = label_name
        self.created_by = created_by
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.info = info

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
                    "SELECT id, label_name, created_by, sample_range, info "
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
                )
                for result in records
            ]

    @staticmethod
    def select_from_dataset_id_and_label_name(dataset_id, label_name, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, created_by, sample_range, info "
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
            )
