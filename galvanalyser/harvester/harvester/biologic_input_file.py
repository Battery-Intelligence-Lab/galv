import os
import ntpath
import copy
from galvani import BioLogic
from galvani.BioLogic import VMPdata_colID_dtype_map, VMPdata_colID_flag_map
import pygalvanalyser.util.battery_exceptions as battery_exceptions
from pygalvanalyser.experiment.input_file import InputFile
from pygalvanalyser.experiment.timeseries_data_row import (
    RECORD_NO_COLUMN_ID,
    TEST_TIME_COLUMN_ID,
    VOLTAGE_COLUMN_ID,
    AMPS_COLUMN_ID,
    ENERGY_CAPACITY_COLUMN_ID,
    CHARGE_CAPACITY_COLUMN_ID,
    TEMPERATURE_COLUMN_ID,
    STEP_TIME_COLUMN_ID,
)

class BiologicMprInputFile(InputFile):
    """
        A class for handling input files
    """

    def __init__(self, file_path):
        if not file_path.endswith(".mpr"):
            raise battery_exceptions.UnsupportedFileTypeError
        self.mpr_file = BioLogic.MPRfile(file_path)
        super().__init__(file_path)

    def get_file_column_to_standard_column_mapping(self):
        """
            Return a dict with a key of the column name in the file that maps to
            the standard column name in the value. Only return values where a
            mapping exists
        """
        return {
            "I/mA": AMPS_COLUMN_ID,
            "Ewe/V": VOLTAGE_COLUMN_ID,
            "time/s": TEST_TIME_COLUMN_ID,
            "Energy/W.h": ENERGY_CAPACITY_COLUMN_ID,
        }

    def load_data(self, file_path, columns, column_renames=None):
        print('load_data from columns', columns)
        new_column_names_to_idx = copy.copy(self.column_names_to_idx)

        if column_renames is not None:
            for name, new_name in column_renames.items():
                new_column_names_to_idx[new_name] = \
                    self.column_names_to_idx[name]
                del new_column_names_to_idx[name]

        for row in self.mpr_file.data:
            yield {
                name: row[col_idx]
                for name, col_idx in new_column_names_to_idx.items()
            }

    def load_metadata(self):
        file_path = self.file_path
        metadata = {}
        metadata["Machine Type"] = "BioLogic"
        metadata["Dataset Name"] = \
            os.path.splitext(ntpath.basename(file_path))[0]
        metadata["Date of Test"] = self.mpr_file.startdate

        num_cols = len(self.mpr_file.data[0])
        VMPdata_colID_map = {}
        VMPdata_colID_map.update(VMPdata_colID_dtype_map)
        VMPdata_colID_map.update(VMPdata_colID_flag_map)

        self.column_names_to_idx = {}
        for k, v in VMPdata_colID_map.items():
            if k < num_cols:
                self.column_names_to_idx[v[0]] = k

        columns_with_data = {
            name: {"has_data": True, "is_numeric": True}
            for name in self.column_names_to_idx.keys()
        }
        metadata["num_rows"] = len(self.mpr_file.data)
        metadata["first_sample_no"] = 1
        metadata["last_sample_no"] = metadata["num_rows"]
        print(metadata, columns_with_data)
        return metadata, columns_with_data

