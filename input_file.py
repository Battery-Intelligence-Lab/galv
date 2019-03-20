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
        self.type = identify_file(file_path)
        self.columns_with_data = identify_columns(self.type, file_path)
        self.metadata = load_metadata(self.type, file_path)

