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

import battery_exceptions
import maccor_functions


def load_metadata(file_type, file_path):
    """
        Reads metadata contained in the file
    """
    if "MACCOR" in file_type:
        if "EXCEL" in file_type:
            return maccor_functions.load_metadata_maccor_excel(file_path)
        else:
            return maccor_functions.load_metadata_maccor_text(file_type,
                                                              file_path)
    else:
        raise battery_exceptions.UnsupportedFileTypeError


def identify_columns(file_type, file_path):
    """
        Identifies which columns are present in the file and which have data
    """
    if "MACCOR" in file_type:
        if "EXCEL" in file_type:
            return maccor_functions.identify_columns_maccor_excel(file_path)
        else:
            return maccor_functions.identify_columns_maccor_text(file_type,
                                                                 file_path)
    else:
        raise battery_exceptions.UnsupportedFileTypeError


def identify_file(file_path):
    """
        Returns a string identifying the type of the input file
    """
    if file_path.endswith('.xls'):
        return "EXCEL-MACCOR"
    elif file_path.endswith('.csv'):
        return "CSV-MACCOR"
    elif file_path.endswith('.txt'):
        return "TSV-MACCOR"
    else:
        raise battery_exceptions.UnsupportedFileTypeError


class InputFile:
    """
        A class for handling input files
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.type = identify_file(file_path)
        self.columns_with_data = identify_columns(self.type, file_path)
        self.metadata = load_metadata(self.type, file_path)

    def get_desired_data(self, standardized_columns):
        """
            Given a list of standard column names return a dict with a key
            for each standard column present in the file and a value for each
            key that is a list of data that mapped to that standard column
        """
        available_columns = self.get_column_to_standard_column_mapping(
                                    standardized_columns)
        if "MACCOR" in self.type:
            if "EXCEL" in self.type:
                return maccor_functions.load_data_maccor_excel(self.file_path,
                                                               available_columns)
            else:
                return maccor_functions.load_data_maccor_text(self.type,
                                                               self.file_path,
                                                               available_columns)
        else:
            raise battery_exceptions.UnsupportedFileTypeError

    def get_column_to_standard_column_mapping(self, standardized_columns):
        """
            Given a list of standard column names return a dict with a key
            of the column name in the file that maps to the standard column
            name in the value. Only return values where a valid mapping exists
        """
        fullmap = {}
        if 'MACCOR' in self.type:
            fullmap = maccor_functions.get_maccor_column_to_standard_column_mapping(standardized_columns)
        available_columns = {key for key, value in
                             self.columns_with_data.items() if value}
        matching_columns = available_columns & set(fullmap.keys())
        return {key: fullmap[key] for key in matching_columns}

