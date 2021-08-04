import os
import ntpath
import copy
from galvani import BioLogic
from galvani.BioLogic import VMPdata_colID_dtype_map, VMPdata_colID_flag_map
from galvanalyser.database.util.battery_exceptions import UnsupportedFileTypeError
from galvanalyser.database.experiment.input_file import InputFile
from galvanalyser.database.experiment.timeseries_data_row import (
    RECORD_NO_COLUMN_ID,
    TEST_TIME_COLUMN_ID,
    VOLTAGE_COLUMN_ID,
    AMPS_COLUMN_ID,
    ENERGY_CAPACITY_COLUMN_ID,
    CHARGE_CAPACITY_COLUMN_ID,
    TEMPERATURE_COLUMN_ID,
    STEP_TIME_COLUMN_ID,
    IMPEDENCE_MAG_COLUMN_ID,
    IMPEDENCE_PHASE_COLUMN_ID,
    FREQUENCY_COLUMN_ID,
)
from galvanalyser.database.experiment.unit import Unit


class BiologicMprInputFile(InputFile):
    """
        A class for handling input files
    """

    def __init__(self, file_path):
        if not file_path.endswith(".mpr"):
            raise UnsupportedFileTypeError
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
            "Q charge/discharge/mA.h": CHARGE_CAPACITY_COLUMN_ID,
            "Aux": TEMPERATURE_COLUMN_ID,
            "|Z|/Ohm": IMPEDENCE_MAG_COLUMN_ID,
            "Phase(Z)/deg": IMPEDENCE_PHASE_COLUMN_ID,
            "freq/Hz": FREQUENCY_COLUMN_ID,
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
            for unit in Unit.get_all_units():
                if name[-len(unit):] == unit:
                    data['unit'] = unit

        metadata["num_rows"] = len(self.mpr_file.data)
        metadata["first_sample_no"] = 1
        metadata["last_sample_no"] = metadata["num_rows"]
        print(metadata, columns_with_data)
        return metadata, columns_with_data
