# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import os
import ntpath
import re
from datetime import datetime
from .input_file import InputFile
from .exceptions import (
    UnsupportedFileTypeError,
    InvalidDataInFileError,
)

IDF_HEADER = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x00\x00\x00\r\x00Version=11'


class IviumInputFile(InputFile):
    """
        A class for handling input files
    """

    def __init__(self, file_path, **kwargs):
        self.validate_file(file_path)
        super().__init__(file_path, **kwargs)
        self.logger.info("Type is IVIUM")

    def get_file_column_to_standard_column_mapping(self) -> dict:
        """
            Return a dict with a key of the column name in the file that maps to
            the standard column name in the value. Only return values where a
            mapping exists
        """
        self.logger.debug("get_ivium_column_to_standard_column_mapping")
        return {
            "amps": self.standard_columns['Amps'],
            "volts": self.standard_columns['Volts'],
            "test_time": self.standard_columns['Time']
        }

    def load_data(self, file_path, columns):
        """
            Load data in a ivium text file"
        """

        with open(file_path, "rb") as f:
            for i in range(self._sample_rows[0]):
                line = f.readline()
            columns_of_interest = []
            column_names = ["test_time", "amps", "volts"]
            for col_idx, column_name in enumerate(column_names):
                if column_name in columns:
                    columns_of_interest.append(col_idx)

            current_line = self._sample_rows[0] - 1
            for sample_row in self._sample_rows:
                while current_line != sample_row:
                    line = f.readline()
                    current_line += 1
                line = line.decode('ascii')

                if len(line) != 40:
                    self.logger.debug(line)
                    raise InvalidDataInFileError(
                        (
                            "Incorrect line length on line {} was {} expected {}"
                        ).format(current_line, len(line), 40)
                    )
                row = [line[:12].strip(), line[13:25].strip(), line[26:].strip()]
                yield {
                    column_names[col_idx]: row[col_idx]
                    for col_idx in columns_of_interest
                }

    def _get_end_task_function(self, task):
        def duration(row):
            return row['test_time'] > task['Duration']

        def E_greater_than(row):
            return row['volts'] > task['E>']

        def E_less_than(row):
            return row['volts'] < task['E<']

        def I_greater_than(row):
            return row['amps'] > task['I<']

        def I_less_than(row):
            return row['amps'] < task['I<']

        end_funcs = []
        for end_key in ['End1', 'End2', 'End3', 'End4']:
            end = task[end_key]
            if end == 'Duration':
                end_funcs.append(duration)
            elif end == 'E>':
                end_funcs.append(E_greater_than)
            elif end == 'E<':
                end_funcs.append(E_less_than)
            elif end == 'I>':
                end_funcs.append(I_greater_than)
            elif end == 'I<':
                end_funcs.append(I_less_than)
            elif end == 'select':
                continue
            else:
                raise UnsupportedFileTypeError(
                    'task end condition {} unknown'.format(end)
                )

        def is_end_task(row):
            is_end = False
            for f in end_funcs:
                is_end |= f(row)
            return is_end

        return is_end_task

    def get_data_labels(self):
        column_names = ["test_time", "amps", "volts"]
        task_index = 0
        current_task = self._file_metadata['Tasks'][task_index]
        is_end_task = self._get_end_task_function(current_task)
        start_task_row = 0
        end_task_row = 0

        prev_time = 0
        for row in self.load_data(self.file_path, column_names):
            end_task_row += 1
            if is_end_task(row):
                time = float(row.get("test_time"))
                mode = current_task.get("Mode")
                if mode.casefold() == "ocp":
                    experiment_label = "Rest "
                else:
                    if mode.casefold() == "cc":
                        key = "amps"
                        units = "A"
                    else:
                        key = "volts"
                        units = "V"

                    control = float(row.get(key))
                    if control > 0:
                        experiment_label = f"Charge "
                    else:
                        experiment_label = f"Discharge "

                    experiment_label += f"at {control} {units} "
                experiment_label += f"for {time - prev_time} seconds"
                if prev_time > time:
                    experiment_label = ""

                yield (
                    f"task_{task_index}_{mode}", (start_task_row, end_task_row), experiment_label
                )

                prev_time = time
                task_index += 1
                if task_index < len(self._file_metadata['Tasks']):
                    current_task = self._file_metadata['Tasks'][task_index]
                    is_end_task = self._get_end_task_function(current_task)
                    start_task_row = end_task_row
                else:
                    break

    def _load_ivium_metadata(self):
        file_path = self.file_path
        regex_key_array = re.compile(r'([^,\[]+)\[([0-9]+)\]$')
        match_sci_notation = re.compile(
            r'[+\-]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)?')
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
                                raise UnsupportedFileTypeError(
                                    'Tasks entry should be a list:', keys[1]
                                )
                            key = array_index_match.group(1)
                            index = int(array_index_match.group(2)) - 1
                            if index < len(base_metadata):
                                base_metadata[index][key] = key_value[1]
                            else:
                                raise UnsupportedFileTypeError(
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
                                raise UnsupportedFileTypeError(
                                    'Data Options.AnalogInputData entry should be a list:', keys[2]
                                )
                            key = array_index_match.group(1)
                            index = int(array_index_match.group(2)) - 1
                            if index < len(base_metadata):
                                base_metadata[index][key] = key_value[1]
                    else:
                        raise UnsupportedFileTypeError(
                            'found unexpected # of keys'
                        )

                else:
                    # check if we've parsed the file ok
                    if not 'Mconfig' in ivium_metadata:
                        raise UnsupportedFileTypeError(
                            'found unexpected line', line
                        )
                    # looks ok, check samples start where we expect them to
                    for i in range(4):
                        line = f.readline().decode('ascii', errors='replace')
                        line = line.replace('\n', '').replace('\r', '')
                        samples_start += 1
                    if len(match_sci_notation.findall(line)) != 3:
                        raise UnsupportedFileTypeError(
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
            'amps': {
                'has_data': True,
                'is_numeric': True,
                'unit': 'A',
            },
            'volts': {
                'has_data': True,
                'is_numeric': True,
                'unit': 'V',
            },
            'test_time': {
                'has_data': True,
                'is_numeric': True,
                'unit': 's',
            },
        }

        # number of samples is total line count minus sample start, minus last line
        metadata["num_rows"] = len(self._sample_rows)
        metadata["first_sample_no"] = 1
        # if sample number not provided by file then we count from 0
        metadata["last_sample_no"] = len(self._sample_rows) - 1
        self.logger.debug(metadata)
        # put in all the ivium metadata
        metadata["misc_file_data"] = dict(self._file_metadata)
        return metadata, columns_with_data

    def validate_file(self, file_path):
        if not file_path.endswith(".idf"):
            raise UnsupportedFileTypeError
        with open(file_path, "rb") as f:
            line = f.readline()
            if not line.startswith(IDF_HEADER):
                raise UnsupportedFileTypeError(
                    'incorrect header - {}'.format(line)
                )
