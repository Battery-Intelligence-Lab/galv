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

import csv

class UnsupportedFileTypeError(Exception):
    """
        Exception indicating the file is unsupported
    """
    pass


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
        raise UnsupportedFileTypeError

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def identify_columns_maccor_excel(file_path):
    """
        Identifies columns in a maccor excel file"
    """
    import xlrd
    with xlrd.open_workbook(file_path, on_demand=True) as wbook:
        sheet = wbook.sheet_by_index(0)
        column_has_data = [False for col in range(0, sheet.ncols)]
        headers = []
        numeric_columns = []
        for col in range(0, sheet.ncols):
            headers.append(sheet.cell_value(1, col))
            if isfloat(sheet.cell_value(2, col)):
                numeric_columns.append(col)
            else:
                column_has_data[col] = True
        print(headers)
        print(numeric_columns)
        for sheet_id in range(0, wbook.nsheets):
            print('Loading sheet ' + str(sheet_id))
            sheet = wbook.sheet_by_index(sheet_id)
            for row in range(2, sheet.nrows):
                for column in numeric_columns[:]:
                    if float(sheet.cell_value(row, column)) != 0.0:
                        column_has_data[column] = True
                        numeric_columns.remove(column)
                        print("Found data in col " + str(column) + " : " +
                              str(float(sheet.cell_value(row, column))))
            print('Unloading sheet ' + str(sheet_id))
            wbook.unload_sheet(sheet_id)
        columns_with_data = {headers[i]: column_has_data[i]
                             for i in range(0, len(headers))}
        print(columns_with_data)
        return columns_with_data


def identify_columns_maccor_text(file_type, file_path):
    """
        Identifies columns in a maccor excel file"
    """
    with open(file_path, 'rb') as csvfile:
        first = csvfile.readline()
        print(first)
        second = csvfile.readline()
        print(second)
        reader = None
        if 'CSV' in file_type:
            reader = csv.reader(csvfile, delimiter=',')
        elif 'TSV' in file_type:
            reader = csv.reader(csvfile, delimiter='\t')
        headers = reader.next()
        column_has_data = [False for column in headers]
        first_data = reader.next()
        column_is_numeric = [isfloat(column) for column in first_data]
        print(column_is_numeric)
        numberic_columns = []
        for i in range(0,len(column_is_numeric)):
            if column_is_numeric[i]:
                numberic_columns.append(i)
            else:
                column_has_data[i] = True
        for row in reader:
            for col in numberic_columns[:]:
                if float(row[col]) != 0.0:
                    column_has_data[col] = True
                    numberic_columns.remove(col)
                    print("Found data in col " + str(col) + " : " + row[col] +
                          " as float: " + str(float(row[col])))
        columns_with_data = {headers[i]: column_has_data[i]
                             for i in range(0, len(headers))}
        print(columns_with_data)
        return columns_with_data

def identify_columns(file_type, file_path):
    """
        Identifies which columns are present in the file and which have data
    """
    if "MACCOR" in file_type:
        if "EXCEL" in file_type:
            return identify_columns_maccor_excel(file_path)
        else:
            return identify_columns_maccor_text(file_type, file_path)
    else:
        raise UnsupportedFileTypeError

class InputFile:
    """
        A class for handling input files
    """

    def __init__(self, file_path):
        self.type = identify_file(file_path)
        self.columns_with_data = identify_columns(self.type, file_path)

