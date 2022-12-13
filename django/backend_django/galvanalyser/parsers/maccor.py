import csv
import pathlib
import re
import os
import ntpath
import maya

from .classes import Parser, FileParseError


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


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


def handle_recno(row, correct_number_of_columns, recno_col, row_idx):
    """
    Ensure the record number is represented in the right place in the column
    """
    if len(row) > correct_number_of_columns:
        if recno_col >= 0:
            row = (
                row[0:recno_col]
                + [(row[recno_col] + row[recno_col + 1]).replace(",", "")]
                + row[recno_col + 2:]
            )
        else:
            raise FileParseError((
                    "There are more data columns than headers. "
                    f"Row {row_idx} has {len(row)} cols, expected {correct_number_of_columns}"
            ))
    elif recno_col >= 0:
        row[recno_col] = row[recno_col].replace(",", "")
    return row


def regularise_column_name(column_name: str) -> str:
    if column_name == "Amp-hr":
        return "Charge Capacity"
    if column_name == "Amps":
        return "Amps"
    if column_name == "Watt-hr":
        return "Energy Capacity"
    if column_name == "StepTime":
        return "Step Time"
    if column_name == "Step (Sec)":
        return "Step Time"
    if column_name == "Volts":
        return "Volts"
    if column_name == "TestTime":
        return "Time"
    if column_name == "Test (Sec)":
        return "Time"
    if column_name == "Rec#":
        return "Sample Number"
    if column_name == "Temp 1":
        return "Temperature"
    return column_name


class MaccorTextFile(Parser):
    extensions = ['csv', 'txt']
    header_row_count = 2
    delimiter = None

    def __init__(self, path: pathlib.Path):
        super(MaccorTextFile, self).__init__(path)
        self.path = "/usr/data/ocrsecio/TPG1+-+Cell+15+-+002.txt"
        if not self.validate_file():
            raise FileParseError(f"File {path} is not a Maccor text file")
        self.regularised_column_names = []
        with open(self.path, 'r') as f:
            r = csv.reader(f, delimiter=self.delimiter)
            first = next(r)
            key = clean_key(first[0])
            self.metadata[key] = maya.parse(first[1]).datetime()
            second = next(r)
            key = clean_key(second[0])
            self.metadata[key] = maya.parse(second[1]).datetime()
            self.metadata["Dataset Name"] = os.path.splitext(
                ntpath.basename(self.path)
            )[0]
            self.metadata["Machine Type"] = "Maccor"
            headers = [header for header in next(r) if header != ""]
            correct_number_of_columns = len(headers)
            try:
                recno_col = headers.index("Rec#")
            except ValueError:
                recno_col = -1
            column_has_data = [False for column in headers]
            row_idx = 1
            first_data = next(r)
            first_data = handle_recno(
                first_data, correct_number_of_columns, recno_col, row_idx
            )
            column_is_numeric = [isfloat(column) for column in first_data]
            numeric_columns = []
            for i in range(0, len(column_is_numeric)):
                if column_is_numeric[i]:
                    numeric_columns.append(i)
                else:
                    column_has_data[i] = True
            for row_idx, row in enumerate(r, 1):
                row = handle_recno(row, correct_number_of_columns, recno_col, row_idx)
                for col in numeric_columns[:]:
                    is_float = True
                    try:
                        data_detected = float(row[col]) != 0.0
                    except ValueError:
                        # Failed to cast a string to float so it is a value
                        column_is_numeric[col] = False
                        data_detected = True
                        is_float = False
                    if data_detected:
                        column_has_data[col] = True
                        numeric_columns.remove(col)
                        print(
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

            self.column_info = [
                {
                    "index": i,
                    "name": headers[i],
                    "regularised_name": regularise_column_name(headers[i]),
                    "has_data": column_has_data[i],
                    "is_numeric": column_is_numeric[i]
                }
                for i in range(0, len(headers))
            ]
            self.metadata["num_rows"] = row_idx + 1  # account for 0-based indexing
            if recno_col == -1:
                # No Rec# , make up numbers
                self.metadata["first_sample_no"] = 1  # Maccor count from 1
                self.metadata["last_sample_no"] = self.metadata["num_rows"]
            else:
                self.metadata["first_sample_no"] = int(first_data[recno_col])
                self.metadata["last_sample_no"] = int(row[recno_col])
        self.ready = True

    def read(self, populated_columns_only: bool = False):
        if populated_columns_only:
            columns = [c for c in self.column_info if c['has_data']]
        else:
            columns = self.column_info
        with open(self.path, 'r') as f:
            r = csv.reader(f, delimiter=self.delimiter)
            for i, row in enumerate(r):
                if i <= self.header_row_count:
                    continue
                yield {
                    columns[i]['regularised_name']:
                        float(row[columns[i]['index']]) if columns[i]['is_numeric'] else row[columns[i]['index']]
                    for i in range(len(columns))
                }

    def validate_file(self) -> bool:
        for delimiter in [',', '\t']:
            with open(self.path, "r") as f:
                line = f.readline()
                line_start = "Today''s Date" + delimiter
                date_regex = r"\d\d\/\d\d\/\d\d\d\d \d?\d:\d\d:\d\d [AP]M"
                if not line.startswith(line_start):
                    continue
                if not re.match((line_start + date_regex), line):
                    continue
                line = f.readline()
                line_start = "Date of Test:" + delimiter
                if not line.startswith(line_start):
                    continue
                if not re.match((line_start + date_regex), line):
                    continue
                reader = csv.reader(f, delimiter=delimiter)
                headers = next(reader)
                if (
                    "Amps" not in headers
                    or "Volts" not in headers
                    or "TestTime" not in headers
                ):
                    continue
                self.delimiter = delimiter
                return True
        return False
