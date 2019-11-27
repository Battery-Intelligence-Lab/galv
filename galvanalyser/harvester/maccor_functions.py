#!/usr/bin/env python

# =========================== MRG Copyright Header ===========================
#
# Copyright (c) 2003-2019 University of Oxford. All rights reserved.
# Authors: Mobile Robotics Group, University of Oxford
#          http://mrg.robots.ox.ac.uk
#
# This file is the property of the University of Oxford.
# Redistribution and use in source and binary forms, with or without
# modification, is not permitted without an explicit licensing agreement
# (research or commercial). No warranty, explicit or implicit, provided.
#
# =========================== MRG Copyright Header ===========================
#
# @author Luke Pitt.
#
import os
import csv
import maya
import ntpath
import re
import galvanalyser.harvester.battery_exceptions as battery_exceptions


class LogFilter(object):
    def write(self, *args):
        if len(args) != 1 or not (
            args[0] == "\n"
            or args[0]
            == "WARNING *** OLE2 inconsistency: SSCS size is 0 but SSAT size is non-zero"
        ):
            print("".join(args))

    def writelines(self, *args):
        pass

    def close(self, *args):
        pass


def get_maccor_column_to_standard_column_mapping():
    """
        Return a dict with a key of the column name in the file that maps to 
        the standard column name in the value. Only return values where a
        mapping exists
    """
    print("get_maccor_column_to_standard_column_mapping")
    all_values = {
        "Amp-hr": 5,
        "Amps": 3,
        "Cyc#": None,
        "DPt Time": None,
        "Watt-hr": 4,
        "State": None,
        "Step": None,
        "StepTime": 7,
        "Step (Sec)": 7,
        "Volts": 2,
        "Capacity": None,
        "Energy": None,
        "Power": None,
        "TestTime": 1,
        "Test (Sec)": 1,
        "Rec#": 0,
        "Temp 1": 6,
    }
    print("all_values: " + str(all_values))
    filtered_values = {
        file_col: std_col
        for file_col, std_col in all_values.items()
        if std_col is not None
    }
    print("filtered_values: " + str(filtered_values))
    return filtered_values


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_maccor_raw_file(file_path):
    with open(file_path, "r") as f:
        line = f.readline()
        line_start = "Today's Date"
        if not line.startswith(line_start):
            return False
        line_bits = line.split("\t")
        if not len(line_bits) == 5:
            return False
        date_regex = "\d\d\/\d\d\/\d\d\d\d"
        dates_regex = line_start + " " + date_regex + "  Date of Test:"
        if not re.match(dates_regex, line_bits[0]):
            return False
        if not re.match(date_regex, line_bits[1]):
            return False
        if not line_bits[2] == " Filename:":
            return False
        if not line_bits[4].startswith("Comment/Barcode: "):
            return False
        line = f.readline()
        standard_columns = (
            "Rec#\tCyc#\tStep\tTest (Sec)\tStep (Sec)\tAmp-hr\tWatt-hr\tAmps\t"
            "Volts\tState\tES\tDPt Time"
        )
        if not line.startswith(standard_columns):
            return False
        return True


def is_maccor_text_file(file_path, delimiter):
    with open(file_path, "r") as f:
        line = f.readline()
        line_start = "Today''s Date" + delimiter
        date_regex = "\d\d\/\d\d\/\d\d\d\d \d?\d:\d\d:\d\d [AP]M"
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


def identify_columns_maccor_excel(wbook):
    """
        Identifies columns in a maccor excel file"
    """
    sheet = wbook.sheet_by_index(0)
    column_has_data = [False for col in range(0, sheet.ncols)]
    headers = []
    numeric_columns = []
    column_is_numeric = []
    for col in range(0, sheet.ncols):
        headers.append(sheet.cell_value(1, col))
        is_numeric = isfloat(sheet.cell_value(2, col))
        column_is_numeric.append(is_numeric)
        if is_numeric:
            numeric_columns.append(col)
        else:
            column_has_data[col] = True
    print("headers: {}".format(headers))
    print("numeric_columns: {}".format(numeric_columns))
    try:
        recno_col = headers.index("Rec#")
        first_rec = sheet.cell_value(2, recno_col)
    except ValueError:
        # Don't have record numbers, make them up
        first_rec = 1
    total_rows = 0
    for sheet_id in range(0, wbook.nsheets):
        print("Loading sheet... " + str(sheet_id))
        sheet = wbook.sheet_by_index(sheet_id)
        total_rows += sheet.nrows - 2
        for row in range(2, sheet.nrows):
            for column in numeric_columns[:]:
                if float(sheet.cell_value(row, column)) != 0.0:
                    column_has_data[column] = True
                    numeric_columns.remove(column)
                    print(
                        "Found data in col {} ( {} ) : {}".format(
                            column,
                            headers[column],
                            float(sheet.cell_value(row, column)),
                        )
                    )
        if sheet.nrows > 2:
            # update this each time there is a valid answer since we don't know
            # for sure if the last sheet actually will have data
            try:
                recno_col = headers.index("Rec#")
                last_rec = sheet.cell_value(2, row)
            except ValueError:
                # Don't have record numbers, make them up
                last_rec = total_rows
        print("Unloading sheet " + str(sheet_id))
        wbook.unload_sheet(sheet_id)
    column_info = {
        headers[i]: {
            "has_data": column_has_data[i],
            "is_numeric": column_is_numeric[i],
        }
        for i in range(0, len(headers))
    }
    print(column_info)
    print("Num rows {}".format(total_rows))
    return column_info, total_rows, first_rec, last_rec


def handle_recno(row, correct_number_of_columns, recno_col, row_idx):
    if len(row) > correct_number_of_columns:
        if recno_col >= 0:
            row = (
                row[0:recno_col]
                + [(row[recno_col] + row[recno_col + 1]).replace(",", "")]
                + row[recno_col + 2 :]
            )
        else:
            raise battery_exceptions.InvalidDataInFileError(
                (
                    "There are more data columns than headers. "
                    "Row {} has {} cols, expected {}"
                ).format(row_idx, len(row), correct_number_of_columns)
            )
    elif recno_col >= 0:
        row[recno_col] = row[recno_col].replace(",", "")
    return row


def identify_columns_maccor_text(reader):
    """
        Identifies columns in a maccor csv or tsv file"
    """
    headers = [header for header in next(reader) if header is not ""]
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
    print(column_is_numeric)
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
    column_info = {
        headers[i]: {
            "has_data": column_has_data[i],
            "is_numeric": column_is_numeric[i],
        }
        for i in range(0, len(headers))
    }
    # account for 0 based indexing
    total_rows = row_idx + 1
    if recno_col == -1:
        # No Rec# , make up numbers
        first_rec = 1  # Maccor count from 1
        last_rec = total_rows
    else:
        first_rec = first_data[recno_col]
        last_rec = row[recno_col]
    print(column_info)
    print("Num rows {}".format(total_rows))
    return column_info, total_rows, first_rec, last_rec


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


def load_metadata_maccor_excel(file_path):
    """
        Load metadata in a maccor excel file"
    """
    import xlrd

    metadata = {}
    with xlrd.open_workbook(
        file_path, on_demand=True, logfile=LogFilter()
    ) as wbook:
        sheet = wbook.sheet_by_index(0)
        col = 0
        if sheet.ncols == 0:
            raise battery_exceptions.EmptyFileError()
        while col < sheet.ncols:
            key = sheet.cell_value(0, col)
            if not key:
                break
            key = clean_key(key)
            if "Date" in key:
                metadata[key] = xlrd.xldate.xldate_as_datetime(
                    sheet.cell_value(0, col + 1), wbook.datemode
                )
                print(
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
        metadata["Dataset Name"] = ntpath.basename(metadata["Filename"])
        metadata["misc_file_data"] = {
            "excel format metadata": (dict(metadata), None)
        }
        metadata["Machine Type"] = "Maccor"
        column_info, total_rows, first_rec, last_rec = identify_columns_maccor_excel(
            wbook
        )
        metadata["num_rows"] = total_rows
        metadata["first_sample_no"] = first_rec
        metadata["last_sample_no"] = last_rec
        print(metadata)
        return metadata, column_info


def load_metadata_maccor_text(file_type, file_path):
    """
        Load metadata in a maccor csv or tsv file"
    """
    metadata = {}
    with open(file_path, "r") as csvfile:
        reader = None
        if "CSV" in file_type:
            reader = csv.reader(csvfile, delimiter=",")
        elif "TSV" in file_type:
            reader = csv.reader(csvfile, delimiter="\t")
        first = next(reader)
        key = clean_key(first[0])
        metadata[key] = maya.parse(first[1]).datetime()
        second = next(reader)
        key = clean_key(second[0])
        metadata[key] = maya.parse(second[1]).datetime()
        metadata["Dataset Name"] = os.path.splitext(
            ntpath.basename(file_path)
        )[0]
        metadata["Machine Type"] = "Maccor"
        column_info, total_rows, first_rec, last_rec = identify_columns_maccor_text(
            reader
        )
        metadata["num_rows"] = total_rows
        metadata["first_sample_no"] = first_rec
        metadata["last_sample_no"] = last_rec
        print(metadata)
        return metadata, column_info


def load_metadata_maccor_raw(file_path):
    """
        Load metadata in a maccor raw file"
    """
    metadata = {}
    column_info = {}
    with open(file_path, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")
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
        metadata["misc_file_data"] = {
            "raw format metadata": (dict(metadata), None)
        }
        # Identify columns, what happens with the aux fields?
        ## This question can't be answered for a few months so just make this
        ## parse what we have and leave handling anything different to some
        ## future person
        metadata["Machine Type"] = "Maccor"
        column_info, total_rows, first_rec, last_rec = identify_columns_maccor_text(
            reader
        )
        metadata["num_rows"] = total_rows
        metadata["first_sample_no"] = first_rec
        metadata["last_sample_no"] = last_rec
        print(metadata)

    return metadata, column_info


def load_data_maccor_excel(file_path, columns, column_renames=None):
    """
        Load metadata in a maccor excel file"
    """
    import xlrd

    with xlrd.open_workbook(
        file_path, on_demand=True, logfile=LogFilter()
    ) as wbook:
        sheet = wbook.sheet_by_index(0)
        columns_of_interest = []
        column_names = []
        recno_col = -1
        for col in range(0, sheet.ncols):
            column_name = sheet.cell_value(1, col)
            if column_name in columns:
                columns_of_interest.append(col)
            if column_name == "Rec#":
                recno_col = col
            if column_renames is not None and column_name in column_renames:
                column_name = column_renames[column_name]
            column_names.append(column_name)
        for sheet_id in range(0, wbook.nsheets):
            print("Loading sheet..." + str(sheet_id))
            sheet = wbook.sheet_by_index(sheet_id)
            for row in range(2, sheet.nrows):
                yield {
                    column_names[col_idx]: (
                        sheet.cell_value(row, col_idx)
                        if recno_col != col_idx
                        else sheet.cell_value(row, col_idx).replace(",", "")
                    )
                    for col_idx in columns_of_interest
                }
            print("Unloading sheet " + str(sheet_id))
            wbook.unload_sheet(sheet_id)


def load_data_maccor_text(file_type, file_path, columns, column_renames=None):
    """
        Load data in a maccor csv or tsv file"
    """

    if column_renames is None:
        column_renames = {col: col for col in columns}

    with open(file_path, "r") as csvfile:
        first = csvfile.readline()
        if "RAW" not in file_type:
            second = csvfile.readline()
        reader = None
        if "CSV" in file_type:
            reader = csv.reader(csvfile, delimiter=",")
        elif "TSV" in file_type:
            reader = csv.reader(csvfile, delimiter="\t")
        elif "RAW" in file_type:
            reader = csv.reader(csvfile, delimiter="\t")
        columns_of_interest = []
        column_names = [header for header in next(reader) if header is not ""]
        correct_number_of_columns = len(column_names)
        try:
            recno_col = column_names.index("Rec#")
        except ValueError:
            recno_col = -1
        for col_idx, column_name in enumerate(column_names):
            if column_name in columns:
                columns_of_interest.append(col_idx)
            if column_renames is not None and column_name in column_renames:
                column_names[col_idx] = column_renames[column_name]
        columns_data = [[] for i in columns_of_interest]
        for row_idx, row in enumerate(reader):
            row = handle_recno(
                row, correct_number_of_columns, recno_col, row_idx
            )
            yield {
                column_names[col_idx]: row[col_idx]
                for col_idx in columns_of_interest
            }


def generate_maccor_data_labels(file_type, file_path, column_info):
    columns = [
        column
        for column, info in column_info.items()
        if info["has_data"] or column == "Cyc#"
    ]
    if "EXCEL" in file_type:
        data_generator = load_data_maccor_excel(file_path, columns)
    else:
        data_generator = load_data_maccor_text(file_type, file_path, columns)

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
    for row_idx, row in enumerate(data_generator):
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
        if numeric_start[column] is not None:
            count = numeric_value_counts[column].get(prev_val, -1) + 1
            yield f"{column}_{prev_val}_{count}", (
                numeric_start[column],
                rec_no + 1,
            )
    for column in non_numeric_columns:
        if non_numeric_start[column] is not None:
            count = non_numeric_value_counts[column].get(prev_val, -1) + 1
            yield f"{column}_{prev_val}_{count}", (
                non_numeric_start[column],
                rec_no + 1,
            )
