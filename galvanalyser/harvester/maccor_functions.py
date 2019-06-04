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
        "Amp-hr": None,
        "Amps": "amps",
        "Cyc#": None,
        "DPt Time": None,
        "Watt-hr": None,
        "State": None,
        "Step": None,
        "StepTime": None,
        "Volts": "volts",
        "Capacity": "capacity",
        "Energy": None,
        "Power": None,
        "TestTime": "test_time",
        "Rec#": "sample_no",
        "Temp 1": "temperature",
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
    print(headers)
    print(numeric_columns)
    for sheet_id in range(0, wbook.nsheets):
        print("Loading sheet... " + str(sheet_id))
        sheet = wbook.sheet_by_index(sheet_id)
        for row in range(2, sheet.nrows):
            for column in numeric_columns[:]:
                if float(sheet.cell_value(row, column)) != 0.0:
                    column_has_data[column] = True
                    numeric_columns.remove(column)
                    print(
                        "Found data in col "
                        + str(column)
                        + " ( "
                        + headers[column]
                        + " ) : "
                        + str(float(sheet.cell_value(row, column)))
                    )
        print("Unloading sheet " + str(sheet_id))
        wbook.unload_sheet(sheet_id)
    columns_with_data = {
        headers[i]: {
            "has_data": column_has_data[i],
            "is_numeric": column_is_numeric[i],
        }
        for i in range(0, len(headers))
    }
    print(columns_with_data)
    return columns_with_data


def identify_columns_maccor_text(reader):
    """
        Identifies columns in a maccor csv or tsv file"
    """
    headers = [header for header in next(reader) if header is not ""]
    column_has_data = [False for column in headers]
    first_data = next(reader)
    column_is_numeric = [isfloat(column) for column in first_data]
    print(column_is_numeric)
    numeric_columns = []
    for i in range(0, len(column_is_numeric)):
        if column_is_numeric[i]:
            numeric_columns.append(i)
        else:
            column_has_data[i] = True
    correct_number_of_columns = len(column_is_numeric)
    try:
        recno_col = headers.index("Rec#")
    except ValueError:
        recno_col = -1
    for row_idx, row in enumerate(reader):
        if len(row) > correct_number_of_columns:
            if recno_col >= 0:
                row = (
                    row[0:recno_col]
                    + [row[recno_col] + row[recno_col + 1]]
                    + row[recno_col + 2 :]
                )
            else:
                raise battery_exceptions.InvalidDataInFileError(
                    (
                        "There are more data columns than headers. "
                        "Row {} has {} cols, expected {}"
                    ).format(row_idx, len(row), correct_number_of_columns)
                )
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
    columns_with_data = {
        headers[i]: {
            "has_data": column_has_data[i],
            "is_numeric": column_is_numeric[i],
        }
        for i in range(0, len(headers))
    }
    print(columns_with_data)
    return columns_with_data


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
        Load metadata  in a maccor excel file"
    """
    import xlrd

    metadata = {}
    with xlrd.open_workbook(
        file_path, on_demand=True, logfile=LogFilter()
    ) as wbook:
        sheet = wbook.sheet_by_index(0)
        col = 0
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
        metadata["Machine Type"] = "Maccor"
        metadata["Experiment Name"] = ntpath.basename(metadata["Filename"])
        columns_with_data = identify_columns_maccor_excel(wbook)
        print(metadata)
        return metadata, columns_with_data


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
        metadata["Experiment Name"] = os.path.splitext(
            ntpath.basename(file_path)
        )[0]
        metadata["Machine Type"] = "Maccor"
        columns_with_data = identify_columns_maccor_text(reader)
        print(metadata)
        return metadata, columns_with_data


def load_data_maccor_excel(file_path, columns, column_renames=None):
    """
        Load metadata  in a maccor excel file"
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
        columns_data = [[] for i in columns_of_interest]
        for sheet_id in range(0, wbook.nsheets):
            print("Loading sheet..." + str(sheet_id))
            sheet = wbook.sheet_by_index(sheet_id)
            for row in range(2, sheet.nrows):
                yield {
                    column_names[col_idx]: (
                        row[col_idx]
                        if recno_col != col_idx
                        else row[col_idx].replace(",", "")
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
        second = csvfile.readline()
        reader = None
        if "CSV" in file_type:
            reader = csv.reader(csvfile, delimiter=",")
        elif "TSV" in file_type:
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
            if len(row) > correct_number_of_columns:
                # handle bug in maccor output where cyc# has commas in it
                if recno_col >= 0:
                    row = (
                        row[0:recno_col]
                        + [
                            (row[recno_col] + row[recno_col + 1]).replace(
                                ",", ""
                            )
                        ]
                        + row[recno_col + 2 :]
                    )
                else:
                    raise battery_exceptions.InvalidDataInFileError(
                        (
                            "There are more data columns than headers. "
                            "Row {} has {} cols, expected {}"
                        ).format(row_idx, len(row), correct_number_of_columns)
                    )
            yield {
                column_names[col_idx]: row[col_idx]
                for col_idx in columns_of_interest
            }
