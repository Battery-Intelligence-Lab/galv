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
import pygalvanalyser.util.battery_exceptions as battery_exceptions
from pygalvanalyser.experiment.input_file import InputFile

IDF_HEADER = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x00\x00\x00\r\x00Version=11'

class IviumInputFile(InputFile):
    """
        A class for handling input files
    """

    def __init__(self, file_path):
        self.validate_file(file_path)
        super().__init__(file_path)

    def get_file_column_to_standard_column_mapping(self):
        print("Type is IVIUM")
        """
            Return a dict with a key of the column name in the file that maps to
            the standard column name in the value. Only return values where a
            mapping exists
        """
        print("get_ivium_column_to_standard_column_mapping")
        return {"amps": 3, "volts": 2, "test_time": 1}


    def load_data(self, file_path, columns, column_renames=None):
        """
            Load data in a ivium text file"
        """

        if column_renames is None:
            column_renames = {col: col for col in columns}

        with open(file_path, "rb") as f:
            for i in range(self._sample_rows[0]):
                line = f.readline()
            columns_of_interest = []
            column_names = ["test_time", "amps", "volts"]
            for col_idx, column_name in enumerate(column_names):
                if column_name in columns:
                    columns_of_interest.append(col_idx)
                if column_renames is not None and column_name in column_renames:
                    column_names[col_idx] = column_renames[column_name]

            current_line = self._sample_rows[0] - 1
            for sample_row in self._sample_rows:
                while current_line != sample_row:
                    line = f.readline()
                    current_line += 1
                line = line.decode('ascii')

                if len(line) != 40:
                    print(line)
                    raise battery_exceptions.InvalidDataInFileError(
                        (
                            "Incorrect line length on line {} was {} expected {}"
                        ).format(current_line, len(line), 40)
                    )
                row = [line[:12].strip(), line[13:25].strip(), line[26:].strip()]
                yield {
                    column_names[col_idx]: row[col_idx]
                    for col_idx in columns_of_interest
                }

    def get_data_labels(self):
        for i in []:
            yield i

    def _load_ivium_metadata(self):
        file_path = self.file_path
        regex_key_array = re.compile(r'([^,\[]+)\[([0-9]+)\]$')
        match_sci_notation = re.compile(r'[+\-]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)?')
        with open(file_path, "rb") as f:
            # header
            line = f.readline()
            samples_start = 0
            ivium_metadata = {}

            while True:
                samples_start += 1
                line = f.readline().decode('ascii', errors='replace')
                line = line.replace('\n', '').replace('\r', '')
                key_value = line.split('=')
                if len(key_value) > 1:
                    keys = key_value[0].split('.')
                    if len(keys) == 1:
                        if keys[0] == 'Tasks':
                            ivium_metadata['Tasks'] = [
                                {} for i in range(int(key_value[1]))
                            ]
                        elif key_value[1]:
                            ivium_metadata[keys[0]] = key_value[1]
                        else:
                            ivium_metadata[keys[0]] = {}

                    elif len(keys) == 2:
                        base_metadata = ivium_metadata[keys[0]]

                        if keys[0] == 'Tasks':
                            array_index_match = regex_key_array.search(keys[1])
                            if not array_index_match:
                                raise battery_exceptions.UnsupportedFileTypeError(
                                    'Tasks entry should be a list:', keys[1]
                                )
                            key = array_index_match.group(1)
                            index = int(array_index_match.group(2)) - 1
                            if index < len(base_metadata):
                                base_metadata[index][key] = key_value[1]
                            else:
                                raise battery_exceptions.UnsupportedFileTypeError(
                                    'unexpected array index {} for line {}'.format(
                                        index, line
                                    ))
                        elif keys[0] == 'Data Options' \
                            and keys[1] == 'AnalogInputData':
                            base_metadata[keys[1]] = [
                                {} for i in range(int(key_value[1]))
                            ]
                        else:
                            if not isinstance(base_metadata, dict):
                                ivium_metadata[keys[0]] = {}
                                base_metadata = ivium_metadata[keys[0]]
                            base_metadata[keys[1]] = key_value[1]

                    elif len(keys) == 3:

                        base_metadata = ivium_metadata[keys[0]][keys[1]]
                        if keys[0] == 'Data Options' \
                                and keys[1] == 'AnalogInputData':
                            array_index_match = regex_key_array.search(keys[2])
                            if not array_index_match:
                                raise battery_exceptions.UnsupportedFileTypeError(
                                    'Data Options.AnalogInputData entry should be a list:', keys[2]
                                )
                            key = array_index_match.group(1)
                            index = int(array_index_match.group(2)) - 1
                            if index < len(base_metadata):
                                base_metadata[index][key] = key_value[1]
                    else:
                        raise battery_exceptions.UnsupportedFileTypeError(
                            'found unexpected # of keys'
                        )

                else:
                    # check if we've parsed the file ok
                    if not 'Mconfig' in ivium_metadata:
                        raise battery_exceptions.UnsupportedFileTypeError(
                            'found unexpected line', line
                        )
                    # looks ok, check samples start where we expect them to
                    for i in range(4):
                        line = f.readline().decode('ascii', errors='replace')
                        line = line.replace('\n', '').replace('\r', '')
                        samples_start += 1
                    if len(match_sci_notation.findall(line)) != 3:
                        raise battery_exceptions.UnsupportedFileTypeError(
                            'cannot find samples start', line
                        )
                    # everything looks good, so we can terminate the loop
                    break

            # continue looping through file getting the sample line numbers
            sample_rows = [samples_start]
            line_no = samples_start
            while True:
                line = f.readline()
                line_no += 1
                if line:
                    line = line.decode('ascii', errors='replace')
                    if len(match_sci_notation.findall(line)) == 3:
                        sample_rows.append(line_no)
                else:
                    break

        return sample_rows, ivium_metadata


    def load_metadata(self):
        """
            Load metadata in a ivium_text file"
        """
        self._sample_rows, self._file_metadata = self._load_ivium_metadata()

        file_path = self.file_path
        metadata = {}

        metadata["Machine Type"] = "Ivium"
        metadata["Dataset Name"] = os.path.splitext(ntpath.basename(file_path))[0]
        metadata["Date of Test"] = datetime.strptime(
            self._file_metadata['starttime'],
            r'%d/%m/%Y %H:%M:%S'
        )
        columns_with_data = {
            name: {"has_data": True, "is_numeric": True}
            for name in
            self.get_file_column_to_standard_column_mapping()
        }

        # number of samples is total line count minus sample start, minus last line
        metadata["num_rows"] = len(self._sample_rows)
        metadata["first_sample_no"] = 1
        metadata["last_sample_no"] = len(self._sample_rows)
        print(metadata)
        # put in all the ivium metadata
        metadata["misc_file_data"] = {
                "ivium format metadata": (dict(self._file_metadata), None)
        }
        return metadata, columns_with_data


    def validate_file(self, file_path):
        if not file_path.endswith(".idf"):
            raise battery_exceptions.UnsupportedFileTypeError
        with open(file_path, "rb") as f:
            line = f.readline()
            if not line.startswith(IDF_HEADER):
                raise battery_exceptions.UnsupportedFileTypeError(
                    'incorrect header - {}'.format(line)
                )




