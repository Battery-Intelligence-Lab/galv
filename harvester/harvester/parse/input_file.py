# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

from .exceptions import UnsupportedFileTypeError
import traceback
from ..settings import get_logger

# see https://gist.github.com/jsheedy/ed81cdf18190183b3b7d
# https://stackoverflow.com/a/30721460


class InputFile:
    """
        A class for handling input files
    """
    unit_conversion_multipliers = {
        'mA': 1e-3,
        'mA.h': 1e-3
    }

    def __init__(self, file_path, standard_columns: dict, standard_units: dict):
        self.file_path = file_path
        self.standard_columns = standard_columns
        self.standard_units = standard_units
        self.logger = get_logger(f"InputFile({self.file_path})")
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
            if self.column_info[col]['unit'] not in self.standard_units:
                raise RuntimeError(
                    "Unknown unit {} provided for standard column mapping"
                    .format(self.column_info[col]['unit'])
                )

        columns = [
            (name, name_to_type_id.get(name, -1))
            for name, info in self.column_info.items()
            if info['has_data'] and info['is_numeric']
        ]

        return columns

    def get_test_start_date(self):
        return self.metadata["Date of Test"]

    def convert_unit(self, name, value):
        if 'unit' in self.column_info[name] and self.column_info[name]['unit'] in self.unit_conversion_multipliers:
            return value * self.unit_conversion_multipliers[self.column_info[name]['unit']]
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
        type_id_to_col_id = {
            name_to_type_id[name]: col_id
            for name, col_id in column_name_to_id.items()
        }

        sample_col_id = type_id_to_col_id.get(self.standard_columns['Sample Number'], None)

        # reconstruct previous row mapping col ids to values
        if last_values is not None:
            previous_row = {
                tsdr.column_id: tsdr.value for tsdr in last_values
            }
            last_rec_no = last_values[0].sample_no
        else:
            previous_row = {}
            for name, col_id in column_name_to_id.items():
                previous_row[col_id] = 0.0
            last_rec_no = -1

        # The psycopg2 cursor.copy_from method needs null values to be
        # represented as a literal '\N'
        def tsv_format(value):
            return str(value) if value is not None else "\\N"

        try:
            for index, row_with_names in enumerate(self.load_data(
                self.file_path, name_to_type_id.keys()
            )):
                # convert dict mapping names to values to dict
                # of col_id => value, use unit info
                # to convert to database units
                row = {
                    column_name_to_id[name]: self.convert_unit(name, value)
                    for name, value in row_with_names.items()
                }

                # get the current sample number
                rec_no = int(row.get(sample_col_id, index))
                if rec_no <= last_rec_no:
                    continue

                # yield the new timeseries_data row
                for col_id, value in row.items():
                    if col_id == sample_col_id:
                        continue
                    timeseries_data_row = [
                        rec_no,
                        col_id,
                        value,
                    ]
                    yield "\t".join(map(tsv_format, timeseries_data_row))
                previous_row = row

        except:
            traceback.print_exc()
            raise

    def load_data(self, file_path, available_desired_columns):
        raise UnsupportedFileTypeError()

    def get_data_labels(self):
        raise UnsupportedFileTypeError()

    def get_file_column_to_standard_column_mapping(self):
        """
            returns map of file column name strings to column id numbers
        """
        raise UnsupportedFileTypeError()

    def load_metadata(self):
        raise UnsupportedFileTypeError()
