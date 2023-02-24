# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import os
import ntpath
from galvani import BioLogic
from .exceptions import UnsupportedFileTypeError
from .input_file import InputFile


class BiologicMprInputFile(InputFile):
    """
        A class for handling input files
    """

    def __init__(self, file_path, **kwargs):
        if not file_path.endswith(".mpr"):
            raise UnsupportedFileTypeError
        self.mpr_file = BioLogic.MPRfile(file_path)
        super().__init__(file_path, **kwargs)
        self.logger.info("Type is BioLogic")

    def get_file_column_to_standard_column_mapping(self) -> dict:
        """
        Return a dict with a key of the column name in the file that maps to
        the standard column name in the value. Only return values where a
        mapping exists
        """
        return {
            "I/mA": self.standard_columns['Amps'],
            "Ewe/V": self.standard_columns['Volts'],
            "time/s": self.standard_columns['Time'],
            "Energy/W.h": self.standard_columns['Energy Capacity'],
            "Q charge/discharge/mA.h": self.standard_columns['Charge Capacity'],
            "Aux": self.standard_columns['Temperature'],
            "|Z|/Ohm": self.standard_columns['Impedence Magnitude'],
            "Phase(Z)/deg": self.standard_columns['Impedence Phase'],
            "freq/Hz": self.standard_columns['Frequency'],
        }

    def load_data(self, file_path, columns):
        columns_of_interest = []
        column_names = list(self.mpr_file.data.dtype.names)
        for col_idx, column_name in enumerate(column_names):
            if column_name in columns:
                columns_of_interest.append(col_idx)
        for row in self.mpr_file.data:
            yield {
                column_names[col_idx]: row[col_idx]
                for col_idx in columns_of_interest
            }

    def get_data_labels(self):
        modes = self.mpr_file.get_flag('mode')
        Ns_changes = self.mpr_file.get_flag('Ns changes')
        Ns_index = self.mpr_file.data.dtype.names.index('Ns')
        mode_labels = {
            1: 'CC',
            2: 'CV',
            3: 'Rest',
        }
        last_Ns_change = 1
        for i in range(len(self.mpr_file.data)):
            last_mode = modes[i-1]
            last_Ns = self.mpr_file.data[i-1][Ns_index]
            Ns_change = Ns_changes[i]
            if Ns_change:
                if last_mode in mode_labels:
                    yield (
                        'Ns_{}_{}'.format(last_Ns,
                                          mode_labels[last_mode]),
                        (last_Ns_change, i-1)
                    )
                else:
                    yield (
                        'Ns_{}'.format(last_Ns),
                        (last_Ns_change, i-1)
                    )
                last_Ns_change = i

    def load_metadata(self):
        file_path = self.file_path
        metadata = {}
        metadata["Machine Type"] = "BioLogic"
        metadata["Dataset Name"] = \
            os.path.splitext(ntpath.basename(file_path))[0]
        metadata["Date of Test"] = self.mpr_file.startdate

        columns_with_data = {
            name: {
                "has_data": True,
                "is_numeric": True,
            }
            for name in self.mpr_file.data.dtype.names
        }
        for name, data in columns_with_data.items():
            for unit in self.standard_units:
                if name[-len(unit):] == unit:
                    data['unit'] = unit

        metadata["num_rows"] = len(self.mpr_file.data)
        # if sample number not provided by file then we count from 0
        metadata["first_sample_no"] = 0
        metadata["last_sample_no"] = metadata["num_rows"] - 1
        self.logger.debug(metadata, columns_with_data)
        return metadata, columns_with_data
