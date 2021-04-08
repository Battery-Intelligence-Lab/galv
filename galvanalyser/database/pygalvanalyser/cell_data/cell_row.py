import psycopg2


class CellRow:
    def __init__(
        self,
        uid,
        manufacturer_id,
        cell_form_factor=None,
        link_to_datasheet=None,
        anode_chemistry=None,
        cathode_chemistry=None,
        nominal_capacity=None,
        nominal_cell_weight=None,
    ):
        self.uid = uid
        self.manufacturer_id = manufacturer_id
        self.cell_form_factor = cell_form_factor
        self.link_to_datasheet = link_to_datasheet
        self.anode_chemistry = anode_chemistry
        self.cathode_chemistry = cathode_chemistry
        self.nominal_capacity = nominal_capacity
        self.nominal_cell_weight = nominal_cell_weight

    def __eq__(self, other):
        if isinstance(other, CellRow):
            return (
                self.uid == other.uid and
                self.manufacturer_id == other.manufacturer_id and
                self.cell_form_factor == other.cell_form_factor and
                self.link_to_datasheet == other.link_to_datasheet and
                self.anode_chemistry == other.anode_chemistry and
                self.cathode_chemistry == other.cathode_chemistry and
                self.nominal_capacity == other.nominal_capacity and
                self.nominal_cell_weight == other.nominal_cell_weight
            )

        return False

    def __repr__(self):
        return ('CellRow({}, {}, {}, {}, {}, {}, {}, {})'
                .format(
                    self.uid,
                    self.manufacturer_id,
                    self.cell_form_factor,
                    self.link_to_datasheet,
                    self.anode_chemistry,
                    self.cathode_chemistry,
                    self.nominal_capacity,
                    self.nominal_cell_weight,
                ))

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO cell_data.cell (uid, "
                    "manufacturer_id, cell_form_factor, "
                    "link_to_datasheet, anode_chemistry, "
                    "cathode_chemistry, nominal_capacity, "
                    "nominal_cell_weight) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                    "RETURNING uid"
                ),
                [
                    self.uid,
                    self.manufacturer_id,
                    self.cell_form_factor,
                    self.link_to_datasheet,
                    self.anode_chemistry,
                    self.cathode_chemistry,
                    self.nominal_capacity,
                    self.nominal_cell_weight,
                ],
            )

    @staticmethod
    def select_from_uid(uid, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT manufacturer_id, cell_form_factor, "
                    "link_to_datasheet, anode_chemistry, "
                    "cathode_chemistry, nominal_capacity, "
                    "nominal_cell_weight FROM "
                    "cell_data.cell "
                    "WHERE uid=(%s)"
                ),
                [uid],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return CellRow(
                uid=uid,
                manufacturer_id=result[0],
                cell_form_factor=result[1],
                link_to_datasheet=result[2],
                anode_chemistry=result[3],
                cathode_chemistry=result[4],
                nominal_capacity=result[5],
                nominal_cell_weight=result[6],
            )
