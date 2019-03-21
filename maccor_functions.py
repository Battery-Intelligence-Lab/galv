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
import maya
import battery_exceptions


class LogFilter(object):
    def write(self, *args):
        if(len(args) != 1 or not ( args[0] == '\n' or args[0] ==
        'WARNING *** OLE2 inconsistency: SSCS size is 0 but SSAT size is non-zero')):
            print(''.join(args))
    def writelines(self, *args):
        pass
    def close(self, *args):
        pass

def get_maccor_column_to_standard_column_mapping(standardized_columns):
    """
        Given a list of standard column names return a dict with a key
        of the column name in the file that maps to the standard column
        name in the value. Only return values where a valid mapping exists
    """
    return {'TestTime': 'timestamp',
            'Volts': 'V',
            'Amps': 'A'}

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
    with xlrd.open_workbook(file_path,
                            on_demand=True,
                            logfile=LogFilter()) as wbook:
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
            print('Loading sheet... ' + str(sheet_id))
            sheet = wbook.sheet_by_index(sheet_id)
            for row in range(2, sheet.nrows):
                for column in numeric_columns[:]:
                    if float(sheet.cell_value(row, column)) != 0.0:
                        column_has_data[column] = True
                        numeric_columns.remove(column)
                        print("Found data in col " + str(column) + " ( " +
                              headers[column] + " ) : " +
                              str(float(sheet.cell_value(row, column))))
            print('Unloading sheet ' + str(sheet_id))
            wbook.unload_sheet(sheet_id)
        columns_with_data = {headers[i]: column_has_data[i]
                             for i in range(0, len(headers))}
        print(columns_with_data)
        return columns_with_data


def identify_columns_maccor_text(file_type, file_path):
    """
        Identifies columns in a maccor csv or tsv file"
    """
    with open(file_path, 'rb') as csvfile:
        first = csvfile.readline()
        second = csvfile.readline()
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
                    print("Found data in col " + str(col) + " ( " +
                          headers[col] + " ) : " + row[col] +
                          " as float: " + str(float(row[col])))
        columns_with_data = {headers[i]: column_has_data[i]
                             for i in range(0, len(headers))}
        print(columns_with_data)
        return columns_with_data

def clean_key(key):
    """
        Unescapes and removes trailing characters on strings
    """
    return key.replace("''", "'").strip().rstrip(':')

def clean_value(value):
    """
        Trims values
    """
    return value.replace("''", "'").strip().rstrip('\0').strip()


def load_metadata_maccor_excel(file_path):
    """
        Load metadata  in a maccor excel file"
    """
    import xlrd
    metadata = {}
    with xlrd.open_workbook(file_path,
                            on_demand=True,
                            logfile=LogFilter()) as wbook:
        sheet = wbook.sheet_by_index(0)
        col = 0
        while col < sheet.ncols:
            key = sheet.cell_value(0, col)
            if not key:
                break
            key = clean_key(key)
            if 'Date' in key:
                metadata[key] = xlrd.xldate.xldate_as_datetime(
                    sheet.cell_value(0, col + 1), wbook.datemode)
                print( "key " + key +" value: " + str(sheet.cell_value(0, col + 1)) +" - datemode: " + str(wbook.datemode))
                col = col + 1
            elif 'Procedure' in key:
                metadata[key] = (clean_value(sheet.cell_value(0, col + 1)) + '\t' +
                                 clean_value(sheet.cell_value(0, col + 2)))
                col = col + 2
            else:
                metadata[key] = sheet.cell_value(0, col + 1)
                col = col + 1
            col = col + 1
    print(metadata)
    return metadata


def load_metadata_maccor_text(file_type, file_path):
    """
        Load metadata in a maccor csv or tsv file"
    """
    metadata = {}
    with open(file_path, 'rb') as csvfile:
        reader = None
        if 'CSV' in file_type:
            reader = csv.reader(csvfile, delimiter=',')
        elif 'TSV' in file_type:
            reader = csv.reader(csvfile, delimiter='\t')
        first = reader.next()
        key = clean_key(first[0])
        metadata[key] = maya.parse(first[1]).datetime()
        second = reader.next()
        key = clean_key(second[0])
        metadata[key] = maya.parse(second[1]).datetime()
    print(metadata)
    return metadata


def load_data_maccor_excel(file_path, columns):
    """
        Load metadata  in a maccor excel file"
    """
    import xlrd
    with xlrd.open_workbook(file_path,
                            on_demand=True,
                            logfile=LogFilter()) as wbook:
        sheet = wbook.sheet_by_index(0)
        columns_of_interest = []
        column_names = []
        for col in range(0, sheet.ncols):
            column_name = sheet.cell_value(1, col)
            column_names.append(column_name)
            if column_name in columns:
                columns_of_interest.append(col)
        columns_data = [[] for i in columns_of_interest]
        for sheet_id in range(0, wbook.nsheets):
            print('Loading sheet...' + str(sheet_id))
            sheet = wbook.sheet_by_index(sheet_id)
            for row in range(2, sheet.nrows):
                for i in range(len(columns_of_interest)):
                    columns_data[i].append(
                        sheet.cell_value(row, columns_of_interest[i]))
            print('Unloading sheet ' + str(sheet_id))
            wbook.unload_sheet(sheet_id)
        return {column_names[columns_of_interest[i]]: columns_data[i]
                for i in range(len(columns_data))}


def load_data_maccor_text(file_type, file_path, columns):
    """
        Load adata in a maccor csv or tsv file"
    """
    with open(file_path, 'rb') as csvfile:
        first = csvfile.readline()
        second = csvfile.readline()
        reader = None
        if 'CSV' in file_type:
            reader = csv.reader(csvfile, delimiter=',')
        elif 'TSV' in file_type:
            reader = csv.reader(csvfile, delimiter='\t')
        columns_of_interest = []
        column_names = reader.next()
        for col in range(len(column_names)):
            if column_names[col] in columns:
                columns_of_interest.append(col)
        columns_data = [[] for i in columns_of_interest]
        for row in reader:
            for i in range(len(columns_of_interest)):
                    columns_data[i].append(row[columns_of_interest[i]])
        return {column_names[columns_of_interest[i]]: columns_data[i]
                for i in range(len(columns_data))}
