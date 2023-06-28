# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import os
import csv
import ntpath
import re
from datetime import datetime
import xlrd
import maya
from .input_file import InputFile
from .exceptions import (
    UnsupportedFileTypeError,
    EmptyFileError,
    InvalidDataInFileError
)


class MaccorInputFile(InputFile):
    """
        A class for handling input files
    """

    def __init__(self, file_path, **kwargs):
        self.validate_file(file_path)
        super().__init__(file_path, **kwargs)
        self.logger.info("Type is MACCOR")

    def identify_columns(self, reader):
        """
            Identifies columns in a maccor csv or tsv file"
        """
        headers = [header for header in next(reader) if header != ""]
        correct_number_of_columns = len(headers)
        try:
            recno_col = headers.index("Rec#")
        except ValueError:
            recno_col = -1
        column_has_data = [False for column in headers]
        row_idx = 1
        first_data = next(reader)
        first_data = handle_recno(
            first_data, correct_number_of_columns, recno_col, row_idx
        )
        column_is_numeric = [isfloat(column) for column in first_data]
        self.logger.debug(column_is_numeric)
        numeric_columns = []
        for i in range(0, len(column_is_numeric)):
            if column_is_numeric[i]:
                numeric_columns.append(i)
            else:
                column_has_data[i] = True
        for row_idx, row in enumerate(reader, 1):
            row = handle_recno(row, correct_number_of_columns, recno_col, row_idx)
            for col in numeric_columns[:]:
                data_detected = False
                is_float = True
                try:
                    data_detected = float(row[col]) != 0.0
                except ValueError:
                    # Failed to cast a string to float so it is a value
                    data_detected = True
                    is_float = False
                if data_detected:
                    column_has_data[col] = True
                    numeric_columns.remove(col)
                    self.logger.debug(
                        "Found data in col {} ( {} ) : {}{} on row {}".format(
                            col,
                            headers[col],
                            row[col],
                            (
                                (" as float: " + str(float(row[col])))
                                if is_float
                                else ""
                            ),
                            row_idx,
                        )
                    )

        column_info = {
            headers[i]: {
                "has_data": column_has_data[i],
                "is_numeric": column_is_numeric[i],
            }
            for i in range(0, len(headers))
        }

        # add unit info for known columns
        known_units = {
            "Amp-hr": 'Amp-hr',
            "Amps": 'Amps',
            "Watt-hr": 'Watt-hr',
            "StepTime": 's',
            "Step (Sec)": 's',
            "Volts": 'Volts',
            "TestTime": 's',
            "Test (Sec)": 's',
            "Rec#": '',
            "Temp 1": 'celsius',
        }
        for name, info in column_info.items():
            if name in known_units:
                column_info[name]['unit'] = known_units[name]

        # account for 0 based indexing
        total_rows = row_idx + 1
        if recno_col == -1:
            # No Rec# , make up numbers
            first_rec = 1  # Maccor count from 1
            last_rec = total_rows
        else:
            first_rec = int(first_data[recno_col])
            last_rec = int(row[recno_col])
        self.logger.debug(column_info)
        self.logger.debug("Num rows {}".format(total_rows))
        return column_info, total_rows, first_rec, last_rec

    def load_metadata(self):
        """
            Load metadata in a maccor csv or tsv file"
        """
        metadata = {}
        with open(self.file_path, "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter)
            self.num_header_rows = 2
            first = next(reader)
            key = clean_key(first[0])
            metadata[key] = maya.parse(first[1]).datetime()
            second = next(reader)
            key = clean_key(second[0])
            metadata[key] = maya.parse(second[1]).datetime()
            metadata["Dataset Name"] = os.path.splitext(
                ntpath.basename(self.file_path)
            )[0]
            metadata["Machine Type"] = "Maccor"
            column_info, total_rows, first_rec, last_rec = \
                self.identify_columns(reader)
            metadata["num_rows"] = total_rows
            metadata["first_sample_no"] = first_rec
            metadata["last_sample_no"] = last_rec
            self.logger.debug(metadata)
            return metadata, column_info

    def get_file_column_to_standard_column_mapping(self) -> dict:
        """
        Return a dict with a key of the column name in the file that maps to
        the standard column name in the value. Only return values where a
        mapping exists

        """
        self.logger.debug("get_maccor_column_to_standard_column_mapping")
        return {
            "Amp-hr": self.standard_columns['Charge Capacity'],
            "Amps": self.standard_columns['Amps'],
            "Watt-hr": self.standard_columns['Energy Capacity'],
            "StepTime": self.standard_columns['Step Time'],
            "Step (Sec)": self.standard_columns['Step Time'],
            "Volts": self.standard_columns['Volts'],
            "TestTime": self.standard_columns['Time'],
            "Test (Sec)": self.standard_columns['Time'],
            "Rec#": self.standard_columns['Sample Number'],
            "Temp 1": self.standard_columns['Temperature']
        }

    def load_data(self, file_path, columns):
        """
            Load data in a maccor csv or tsv file"
        """

        with open(file_path, "r") as csvfile:
            # get rid of metadata rows
            csvfile.readline()
            if self.num_header_rows > 1:
                csvfile.readline()

            # remainder is csv format
            reader = csv.reader(csvfile, delimiter=self.delimiter)
            columns_of_interest = []
            column_names = [header for header in next(reader) if header != ""]
            correct_number_of_columns = len(column_names)
            try:
                recno_col = column_names.index("Rec#")
            except ValueError:
                recno_col = -1
            for col_idx, column_name in enumerate(column_names):
                if column_name in columns:
                    columns_of_interest.append(col_idx)
            for row_idx, row in enumerate(reader):
                row = handle_recno(
                    row, correct_number_of_columns, recno_col, row_idx
                )
                yield {
                    column_names[col_idx]: row[col_idx]
                    for col_idx in columns_of_interest
                }

    def get_data_labels(self):
        file_path = self.file_path
        column_info = self.column_info
        columns = [
            column
            for column, info in column_info.items()
            if info["has_data"] or column == "Cyc#"
        ]
        data_generator = self.load_data(file_path, columns)

        # Generate labels for some specific numeric columns
        numeric_columns = [
            column
            for column, info in column_info.items()
            if column in {"Step", "ES"} and info["is_numeric"]
        ]

        non_numeric_columns = [
            column
            for column, info in column_info.items()
            if info["has_data"] and not info["is_numeric"] and column != "DPt Time"
        ]

        # note ranges returned are inclusive lower bound, exclusive upper bound
        cyc_no = None
        cyc_no_start = None
        cyc_amps = 0
        numeric_value = {column: None for column in numeric_columns}
        numeric_start = {column: 0 for column in numeric_columns}
        numeric_value_counts = {column: {} for column in numeric_columns}
        non_numeric_value = {column: None for column in non_numeric_columns}
        non_numeric_start = {column: 0 for column in non_numeric_columns}
        non_numeric_value_counts = {column: {} for column in non_numeric_columns}
        for row_idx, row in enumerate(data_generator, 1):
            rec_no = int(row.get("Rec#", row_idx))

            # Generate ranges for cycles
            if "Cyc#" in row:
                row_cyc = int(row["Cyc#"])
                if cyc_no is None:
                    cyc_no = row_cyc
                    cyc_no_start = rec_no
                elif cyc_no < row_cyc:
                    # on a new cycle
                    yield "cycle_{}".format(cyc_no), (cyc_no_start, rec_no + 1)
                    cyc_no = row_cyc
                    cyc_no_start = rec_no
            elif "Amps" in row:
                # This file doesn't have cycles recorded, try and detect them from
                # amps
                amps = float(row["Amps"])
                cyc_begin = cyc_amps <= 0 and amps > 0.0
                cyc_mid = cyc_amps > 0 and amps < 0.0
                cyc_end = cyc_amps < 0 and amps >= 0.0
                # a <=0 to positive amps edge
                if cyc_begin:
                    cyc_amps = 1
                    if cyc_no_start is not None:
                        yield "cycle_{}".format(cyc_no), (cyc_no_start, rec_no + 1)
                    cyc_no_start = rec_no
                    cyc_no = 0 if cyc_no is None else cyc_no + 1
                # a <0 to 0 change
                elif cyc_end:  # cycle ended at zero amps, not start of a new cycle
                    yield "cycle_{}".format(cyc_no), (cyc_no_start, rec_no + 1)
                    cyc_no_start = None
                    cyc_amps = 0
                elif cyc_mid:
                    # positive to 0 or negative
                    cyc_amps = -1

            # Handle ranges for specific numeric data
            for column in numeric_columns:
                prev_val = numeric_value[column]
                col_val = row[column]
                # handle first iteration
                if prev_val is None:
                    numeric_value[column] = col_val
                    numeric_start[column] = rec_no
                elif prev_val != col_val:
                    # value has changed, end range
                    count = numeric_value_counts[column].get(prev_val, -1) + 1
                    numeric_value_counts[column][prev_val] = count
                    yield f"{column}_{prev_val}_{count}", (
                        numeric_start[column],
                        rec_no + 1,
                    )
                    numeric_value[column] = col_val
                    numeric_start[column] = rec_no

            # Handle ranges for non-numeric data
            for column in non_numeric_columns:
                prev_val = non_numeric_value[column]
                col_val = row[column]
                # handle first iteration
                if prev_val is None:
                    non_numeric_value[column] = col_val
                    non_numeric_start[column] = rec_no
                elif prev_val != col_val:
                    # value has changed, end range
                    count = non_numeric_value_counts[column].get(prev_val, -1) + 1
                    non_numeric_value_counts[column][prev_val] = count
                    yield f"{column}_{prev_val}_{count}", (
                        non_numeric_start[column],
                        rec_no + 1,
                    )
                    non_numeric_value[column] = col_val
                    non_numeric_start[column] = rec_no

        # return any partial ranges
        if cyc_no_start is not None:
            yield "cycle_{}".format(cyc_no), (cyc_no_start, rec_no + 1)
        for column in numeric_columns:
            prev_val = numeric_value[column]
            if numeric_start[column] is not None:
                count = numeric_value_counts[column].get(prev_val, -1) + 1
                yield f"{column}_{prev_val}_{count}", (
                    numeric_start[column],
                    rec_no + 1,
                )
        for column in non_numeric_columns:
            prev_val = non_numeric_value[column]
            if non_numeric_start[column] is not None:
                count = non_numeric_value_counts[column].get(prev_val, -1) + 1
                yield f"{column}_{prev_val}_{count}", (
                    non_numeric_start[column],
                    rec_no + 1,
                )

    def is_maccor_text_file(self, file_path, delimiter):
        with open(file_path, "r") as f:
            line = f.readline()
            line_start = "Today''s Date" + delimiter
            date_regex = r"\d\d\/\d\d\/\d\d\d\d \d?\d:\d\d:\d\d [AP]M"
            if not line.startswith(line_start):
                return False
            if not re.match((line_start + date_regex), line):
                return False
            line = f.readline()
            line_start = "Date of Test:" + delimiter
            if not line.startswith(line_start):
                return False
            if not re.match((line_start + date_regex), line):
                return False
            reader = csv.reader(f, delimiter=delimiter)
            headers = next(reader)
            if (
                "Amps" not in headers
                or "Volts" not in headers
                or "TestTime" not in headers
            ):
                return False
        return True

    def validate_file(self, file_path):
        if not (
                file_path.endswith(".csv") or
                file_path.endswith(".txt")
        ):
            raise UnsupportedFileTypeError

        self.delimiter = None
        for delim in [',', '\t']:
            if self.is_maccor_text_file(file_path, delim):
                self.delimiter = delim
        if self.delimiter is None:
            raise UnsupportedFileTypeError


class MaccorExcelInputFile(MaccorInputFile):
    """
        A class for handling input files
    """

    def __init__(self, file_path):
        self.validate_file(file_path)
        super().__init__(file_path)

    def identify_columns(self, wbook):
        """
            Identifies columns in a maccor excel file"
        """
        sheet = wbook.sheet_by_index(0)
        column_has_data = [False for col in range(0, sheet.ncols)]
        headers = []
        numeric_columns = []
        column_is_numeric = []
        if self._has_metadata_row:
            headers_row = 1
        else:
            headers_row = 0
        for col in range(0, sheet.ncols):
            headers.append(sheet.cell_value(headers_row, col))
            is_numeric = isfloat(
                sheet.cell_value(headers_row+1, col)
            )
            column_is_numeric.append(is_numeric)
            if is_numeric:
                numeric_columns.append(col)
            else:
                column_has_data[col] = True
        self.logger.debug("headers: {}".format(headers))
        self.logger.debug("numeric_columns: {}".format(numeric_columns))
        try:
            recno_col = headers.index("Rec#")
            first_rec = sheet.cell_value(headers_row+1, recno_col)
        except ValueError:
            # Don't have record numbers, make them up
            first_rec = 1
        total_rows = 0
        for sheet_id in range(0, wbook.nsheets):
            self.logger.debug("Loading sheet... " + str(sheet_id))
            sheet = wbook.sheet_by_index(sheet_id)
            total_rows += sheet.nrows - 1 - int(self._has_metadata_row)
            for row in range(headers_row+1, sheet.nrows):
                for column in numeric_columns[:]:
                    if float(sheet.cell_value(row, column)) != 0.0:
                        column_has_data[column] = True
                        numeric_columns.remove(column)
                        self.logger.debug(
                            "Found data in col {} ( {} ) : {}".format(
                                column,
                                headers[column],
                                float(sheet.cell_value(row, column)),
                            )
                        )
            if sheet.nrows > 2:
                # update this each time there is a valid answer since we don't know for
                # sure if the last sheet actually will have data
                try:
                    recno_col = headers.index("Rec#")
                    last_rec = sheet.cell_value(headers_row+1, row)
                except ValueError:
                    # Don't have record numbers, make them up
                    last_rec = total_rows
            self.logger.debug("Unloading sheet " + str(sheet_id))
            wbook.unload_sheet(sheet_id)

        column_info = {
            headers[i]: {
                "has_data": column_has_data[i],
                "is_numeric": column_is_numeric[i],
            }
            for i in range(0, len(headers))
        }
        self.logger.debug(column_info)
        self.logger.debug("Num rows {}".format(total_rows))
        return column_info, total_rows, first_rec, last_rec

    def load_data(self, file_path,
                  columns, column_renames=None):
        """
            Load metadata in a maccor excel file"
        """
        if self._has_metadata_row:
            headers_row = 1
        else:
            headers_row = 0

        with xlrd.open_workbook(
            file_path, on_demand=True, logfile=LogFilter(self.logger)
        ) as wbook:
            sheet = wbook.sheet_by_index(0)
            columns_of_interest = []
            column_names = []
            recno_col = -1
            for col in range(0, sheet.ncols):
                column_name = sheet.cell_value(headers_row, col)
                if column_name in columns:
                    columns_of_interest.append(col)
                if column_name == "Rec#":
                    recno_col = col
                if column_renames is not None and column_name in column_renames:
                    column_name = column_renames[column_name]
                column_names.append(column_name)
            for sheet_id in range(0, wbook.nsheets):
                self.logger.debug("Loading sheet..." + str(sheet_id))
                sheet = wbook.sheet_by_index(sheet_id)
                for row in range(headers_row+1, sheet.nrows):
                    yield {
                        column_names[col_idx]: (
                            sheet.cell_value(row, col_idx)
                            if recno_col != col_idx
                            else sheet.cell_value(row, col_idx).replace(",", "")
                        )
                        for col_idx in columns_of_interest
                    }
                self.logger.debug("Unloading sheet " + str(sheet_id))
                wbook.unload_sheet(sheet_id)

    def load_metadata(self):
        """
            Load metadata in a maccor excel file"
        """
        metadata = {}
        metadata['Filename'] = self.file_path
        with xlrd.open_workbook(
            self.file_path, on_demand=True, logfile=LogFilter(self.logger)
        ) as wbook:
            sheet = wbook.sheet_by_index(0)
            col = 0
            self._has_metadata_row = True
            if sheet.ncols == 0:
                raise EmptyFileError()
            elif "Cyc#" in sheet.cell_value(0, 0):
                self._has_metadata_row = False
            if self._has_metadata_row:
                while col < sheet.ncols:
                    key = sheet.cell_value(0, col)
                    if not key:
                        break
                    key = clean_key(key)
                    if "Date" in key:
                        metadata[key] = xlrd.xldate.xldate_as_datetime(
                            sheet.cell_value(0, col + 1), wbook.datemode
                        )
                        self.logger.debug(
                            "key "
                            + key
                            + " value: "
                            + str(sheet.cell_value(0, col + 1))
                            + " - datemode: "
                            + str(wbook.datemode)
                        )
                        col = col + 1
                    elif "Procedure" in key:
                        metadata[key] = (
                            clean_value(sheet.cell_value(0, col + 1))
                            + "\t"
                            + clean_value(sheet.cell_value(0, col + 2))
                        )
                        col = col + 2
                    else:
                        metadata[key] = sheet.cell_value(0, col + 1)
                        col = col + 1
                    col = col + 1
                metadata["misc_file_data"] = dict(metadata)
            if "Dataset Name" not in metadata:
                metadata["Dataset Name"] = os.path.splitext(
                    ntpath.basename(self.file_path)
                )[0]
            if "Date of Test" not in metadata:
                metadata["Date of Test"] = datetime.fromtimestamp(
                    os.path.getctime(self.file_path)
                )
            metadata["Machine Type"] = "Maccor"
            column_info, total_rows, first_rec, last_rec = \
                self.identify_columns(wbook)
            metadata["num_rows"] = total_rows
            metadata["first_sample_no"] = first_rec
            metadata["last_sample_no"] = last_rec
            self.logger.debug(metadata)
            return metadata, column_info

    def validate_file(self, file_path):
        if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
            return
        else:
            raise UnsupportedFileTypeError


class MaccorRawInputFile(MaccorInputFile):
    """
        A class for handling input files
    """

    def __init__(self, file_path):
        self.validate_file(file_path)
        super().__init__(file_path)
        self.delimiter = '\t'

    def load_metadata(self):
        """
            Load metadata in a maccor raw file"
        """
        metadata = {}
        column_info = {}
        with open(self.file_path, "r") as csvfile:
            reader = csv.reader(csvfile, delimiter="\t")
            self.num_header_rows = 1
            first = next(reader)
            metadata["Today's Date"] = maya.parse(
                first[0].split(" ")[2], year_first=False
            ).datetime()
            metadata["Date of Test"] = maya.parse(
                first[1], year_first=False
            ).datetime()
            metadata["Filename"] = first[3].split(" Procedure:")[0]
            metadata["Dataset Name"] = ntpath.basename(metadata["Filename"])
            # Just shove everything in the misc_file_data for now rather than
            # trying to parse it
            metadata["File Header Parts"] = first
            metadata["misc_file_data"] = dict(metadata)
            # Identify columns, what happens with the aux fields?
            # This question can't be answered for a few months so just make this
            # parse what we have and leave handling anything different to some
            # future person
            metadata["Machine Type"] = "Maccor"
            column_info, total_rows, first_rec, last_rec = \
                self.identify_columns(reader)
            metadata["num_rows"] = total_rows
            metadata["first_sample_no"] = first_rec
            metadata["last_sample_no"] = last_rec
            self.logger.debug(metadata)

        return metadata, column_info

    def validate_file(self, file_path):
        self.logger.debug('is_maccor_raw_file')
        with open(file_path, "r") as f:
            self.logger.debug('got line')
            line = f.readline()
            self.logger.debug('got line', line)
            line_start = "Today's Date"
            if not line.startswith(line_start):
                raise UnsupportedFileTypeError
            line_bits = line.split("\t")
            if not len(line_bits) == 5:
                raise UnsupportedFileTypeError
            date_regex = "\d\d\/\d\d\/\d\d\d\d"
            dates_regex = line_start + " " + date_regex + "  Date of Test:"
            if not re.match(dates_regex, line_bits[0]):
                raise UnsupportedFileTypeError
            if not re.match(date_regex, line_bits[1]):
                raise UnsupportedFileTypeError
            if not line_bits[2] == " Filename:":
                raise UnsupportedFileTypeError
            if not line_bits[4].startswith("Comment/Barcode: "):
                raise UnsupportedFileTypeError
            line = f.readline()
            standard_columns = (
                "Rec#\tCyc#\tStep\tTest (Sec)\tStep (Sec)\tAmp-hr\tWatt-hr\tAmps\t"
                "Volts\tState\tES\tDPt Time"
            )
            if not line.startswith(standard_columns):
                raise UnsupportedFileTypeError


class LogFilter(object):
    def __init__(self, logger):
        self.logger = logger

    def write(self, *args):
        if len(args) != 1 or not (
            args[0] == "\n"
            or args[0]
            == "WARNING *** OLE2 inconsistency: SSCS size is 0 but SSAT size is non-zero"
        ):
            self.logger.debug("".join(args))

    def writelines(self, *args):
        pass

    def close(self, *args):
        pass


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def handle_recno(row, correct_number_of_columns, recno_col, row_idx):
    if len(row) > correct_number_of_columns:
        if recno_col >= 0:
            row = (
                row[0:recno_col]
                + [(row[recno_col] + row[recno_col + 1]).replace(",", "")]
                + row[recno_col + 2:]
            )
        else:
            raise InvalidDataInFileError(
                (
                    "There are more data columns than headers. "
                    "Row {} has {} cols, expected {}"
                ).format(row_idx, len(row), correct_number_of_columns)
            )
    elif recno_col >= 0:
        row[recno_col] = row[recno_col].replace(",", "")
    return row


def clean_key(key):
    """
        Unescapes and removes trailing characters on strings
    """
    return key.replace("''", "'").strip().rstrip(":")


def clean_value(value):
    """
        Trims values
    """
    return value.replace("''", "'").strip().rstrip("\0").strip()
