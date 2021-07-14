from galvanalyser.database.util.battery_exceptions import UnsupportedFileTypeError
from itertools import accumulate
import traceback
from galvanalyser.database.experiment.timeseries_data_row import (
    RECORD_NO_COLUMN_ID,
    TEST_TIME_COLUMN_ID,
    VOLTAGE_COLUMN_ID,
    AMPS_COLUMN_ID,
    ENERGY_CAPACITY_COLUMN_ID,
    CHARGE_CAPACITY_COLUMN_ID,
    TEMPERATURE_COLUMN_ID,
    STEP_TIME_COLUMN_ID,
    IMPEDENCE_MAG_COLUMN_ID,
    IMPEDENCE_PHASE_COLUMN_ID,
    FREQUENCY_COLUMN_ID,
)
from .unit import Unit

# see https://gist.github.com/jsheedy/ed81cdf18190183b3b7d
# https://stackoverflow.com/a/30721460


class InputFile:
    """
        A class for handling input files
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.metadata, self.column_info = self.load_metadata()

    def get_columns(self):
        name_to_type_id = self.get_file_column_to_standard_column_mapping()

        # verify that every file col has units
        for col, std in name_to_type_id.items():
            if col not in self.column_info:
                continue
            if 'unit' not in self.column_info[col]:
                raise RuntimeError((
                    "Unit not provided for standard column mapping.\n"
                    "file_column_to_standard_column is {}: {}\n"
                    "column_info is {}\n"
                ).format(col, std, self.column_info[col]))
            if self.column_info[col]['unit'] not in Unit.get_all_units():
                raise RuntimeError(
                    "Unknown unit {} provided for standard column mapping"
                    .format(self.column_info[col]['unit'])
                )

        columns = [
            (name, name_to_type_id.get(name, -1))
            for name in self.column_info.keys()
        ]

        # add calculate columns (see complete_columns)
        for calc_col_id in []:
            not_found = True
            for name, col_id in columns:
                if col_id == calc_col_id:
                    not_found = False
                    break
            if not_found:
                columns.append(("Charge Capacity (calculated)",
                                CHARGE_CAPACITY_COLUMN_ID))

        return columns

    def get_test_start_date(self):
        return self.metadata["Date of Test"]

    def complete_columns(self, current_row, previous_row):
        # if CHARGE_CAPACITY_COLUMN_ID not in current_row:
        #    prev_time = previous_row[TEST_TIME_COLUMN_ID]
        #    prev_amps = previous_row[AMPS_COLUMN_ID]
        #    capacity_total = previous_row[CHARGE_CAPACITY_COLUMN_ID]
        #    current_amps = float(current_row[AMPS_COLUMN_ID])
        #    current_time = float(current_row[TEST_TIME_COLUMN_ID])
        #    capacity_total += ((prev_amps + current_amps) / 2.0) * (
        #        current_time - prev_time
        #    )
        #    current_row[CHARGE_CAPACITY_COLUMN_ID] = capacity_total
        #    prev_amps = current_amps
        #    prev_time = current_time
        return current_row

    def convert_unit(self, name, value):
        if 'unit' in self.column_info[name]:
            unit = self.column_info[name]['unit']
            value = Unit.convert(unit, value)
        return value

    def get_data_row_generator(
        self,
        column_name_to_id, last_values=None,
    ):
        # create some useful mappings
        name_to_type_id = {
            name: type_id
            for name, type_id in self.get_columns()
        }

        col_type_id_to_col_id = {
            type_id: column_name_to_id[name]
            for name, type_id in name_to_type_id.items()
        }

        # reconstruct previous row mapping col ids to values
        if last_values is not None:
            previous_row = {
                tsdr.column_type_id: tsdr.value for tsdr in last_values
            }
            if RECORD_NO_COLUMN_ID not in previous_row:
                previous_row[RECORD_NO_COLUMN_ID] = last_values[0].sample_no
        else:
            previous_row = {}
            for name, col_type_id in name_to_type_id.items():
                previous_row[col_type_id] = 0.0

        # The psycopg2 cursor.copy_from method needs null values to be
        # represented as a literal '\N'
        def tsv_format(value):
            return str(value) if value is not None else "\\N"

        try:
            for index, row_with_names in enumerate(self.load_data(
                self.file_path, self.column_info.keys()
            )):
                # convert dict mapping names to values to dict
                # of col_type_id => value, use unit info
                # to convert to database units
                row = {
                    name_to_type_id[name]: self.convert_unit(name, value)
                    for name, value in row_with_names.items()
                }

                # add any missing columns that we can
                row = self.complete_columns(row, previous_row)

                # get the current sample number
                rec_no = row.get(RECORD_NO_COLUMN_ID, index)

                # yield the new timeseries_data row
                for col_type_id, value in row.items():
                    if col_type_id == RECORD_NO_COLUMN_ID:
                        continue
                    timeseries_data_row = [
                        rec_no,
                        col_type_id_to_col_id[col_type_id],
                        value,
                    ]
                    yield "\t".join(map(tsv_format, timeseries_data_row))
                previous_row = row
        except:
            traceback.print_exc()
            raise

    def load_data(self, file_path, available_desired_columns):
        raise UnsupportedFileTypeError

    def get_data_labels(self):
        raise UnsupportedFileTypeError

    def get_file_column_to_standard_column_mapping(self):
        """
            returns map of file column name strings to column id numbers
        """
        raise UnsupportedFileTypeError

    def load_metadata(self):
        raise UnsupportedFileTypeError
