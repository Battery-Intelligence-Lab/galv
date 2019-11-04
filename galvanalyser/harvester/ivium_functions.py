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
from datetime import datetime
import galvanalyser.harvester.battery_exceptions as battery_exceptions


def get_ivium_column_to_standard_column_mapping():
    """
        Return a dict with a key of the column name in the file that maps to 
        the standard column name in the value. Only return values where a
        mapping exists
    """
    print("get_ivium_column_to_standard_column_mapping")
    return {"amps": 3, "volts": 2, "test_time": 1}


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_ivium_text_file(file_path):
    with open(file_path, "r") as f:
        line = f.readline()
        if len(line) != 39:
            return False
        number_regex = "-?\d\.\d{5}E[+-]\d\d ?"
        if not re.match(
            "{} {} {}".format(number_regex, number_regex, number_regex), line
        ):
            return False
    return True


def load_metadata_ivium_text(file_path):
    """
        Load metadata in a ivium_text file"
    """
    metadata = {}
    metadata["Machine Type"] = "Ivium"
    metadata["Dataset Name"] = os.path.splitext(ntpath.basename(file_path))[
        0
    ]
    metadata["Date of Test"] = datetime.fromtimestamp(
        os.path.getctime(file_path)
    )
    columns_with_data = {
        name: {"has_data": True, "is_numeric": True}
        for name in get_ivium_column_to_standard_column_mapping()
    }
    with open(file_path, "r") as f:
        total_rows = sum(1 for line in f)
        metadata["num_rows"] = total_rows
        metadata["first_sample_no"] = 1
        metadata["last_sample_no"] = total_rows
        print(metadata)
        return metadata, columns_with_data


def load_data_ivium_text(file_path, columns, column_renames=None):
    """
        Load data in a ivium text file"
    """

    if column_renames is None:
        column_renames = {col: col for col in columns}

    with open(file_path, "r") as f:
        columns_of_interest = []
        column_names = ["test_time", "amps", "volts"]
        for col_idx, column_name in enumerate(column_names):
            if column_name in columns:
                columns_of_interest.append(col_idx)
            if column_renames is not None and column_name in column_renames:
                column_names[col_idx] = column_renames[column_name]
        for line_idx, line in enumerate(f, 1):
            if len(line) != 39:
                raise battery_exceptions.InvalidDataInFileError(
                    (
                        "Incorrect line length on line {} was {} expected {}"
                    ).format(line_idx, len(line), 39)
                )
            row = [line[:12].strip(), line[13:25].strip(), line[26:].strip()]
            yield {
                column_names[col_idx]: row[col_idx]
                for col_idx in columns_of_interest
            }


def generate_ivium_data_labels(file_type, file_path, columns):
    for item in []:
        yield item
