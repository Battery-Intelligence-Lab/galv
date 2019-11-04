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
    ):
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
                    "VALUES (%s, %s, %s, '[%s, %s)', %s)"
                ),
                [
                    self.dataset_id,
                    self.label_name,
                    self.created_by,
                    self.lower_bound,
                    self.upper_bound,
                    self.info,
                ],
            )

    @staticmethod
    def select_from_dataset_id(dataset_id, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT label_name, created_by, sample_range, info "
                    "FROM experiment.range_label "
                    "WHERE dataset_id=(%s)"
                ),
                [dataset_id],
            )
            records = cursor.fetchall()
            return [
                RangeLabelRow(
                    dataset_id=dataset_id,
                    label_name=result[0],
                    created_by=result[1],
                    lower_bound=result[2].lower,
                    upper_bound=result[2].upper,
                    info=result[3],
                )
                for result in records
            ]

    @staticmethod
    def select_from_dataset_id_and_label_name(dataset_id, label_name, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT created_by, sample_range, info FROM experiment.range_label "
                    "WHERE dataset_id=(%s) AND label_name=(%s)"
                ),
                [dataset_id, label_name],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return RangeLabelRow(
                dataset_id=dataset_id,
                label_name=label_name,
                created_by=result[0],
                lower_bound=result[1][0],
                upper_bound=result[1][1],
                info=result[2],
            )
