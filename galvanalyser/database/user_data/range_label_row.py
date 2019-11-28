import psycopg2


class RangeLabelRow:
    def __init__(
        self,
        dataset_id,
        label_name,
        created_by,
        lower_bound,
        upper_bound,
        access,
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
        self.access = access

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO user_data.range_label "
                    "(dataset_id, label_name, created_by, sample_range, info, "
                    "access) "
                    "VALUES (%s, %s, %s, '[%s, %s)', %s, %s) "
                    "RETURNING id"
                ),
                [
                    self.dataset_id,
                    self.label_name,
                    self.created_by,
                    self.lower_bound,
                    self.upper_bound,
                    self.info,
                    self.access,
                ],
            )
            self.id = cursor.fetchone()[0]
            return cursor.query

    def update(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "UPDATE user_data.range_label SET "
                    "sample_range='[%s, %s)', info=%s "
                    "WHERE dataset_id=%s AND label_name=%s AND created_by=%s"
                ),
                [
                    self.lower_bound,
                    self.upper_bound,
                    self.info,
                    self.dataset_id,
                    self.label_name,
                    self.created_by,
                ],
            )
