# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import os
import psutil

from .database.util.battery_exceptions import UnsupportedFileTypeError

import traceback

from .ivium_input_file import IviumInputFile
from .biologic_input_file import BiologicMprInputFile
from .maccor_input_file import (
    MaccorInputFile,
    MaccorExcelInputFile,
    MaccorRawInputFile,
)

registered_input_files = [
    BiologicMprInputFile,
    IviumInputFile,
    MaccorInputFile,
    MaccorExcelInputFile,
    MaccorRawInputFile,
]


def has_handle(fpath):
    """
        Returns true if the file is in use by a process
    """
    for proc in psutil.process_iter():
        try:
            for item in proc.open_files():
                if fpath == item.path:
                    return True
        except Exception:
            pass

    return False


def import_file(base_path, file_path_row, harvester_name, conn):
    """
        Attempts to import a given file
    """
    absolute_path = file_path_row.monitored_path
    if not os.path.isabs(absolute_path) and base_path is not None:
        absolute_path = os.path.join(base_path, absolute_path)

    fullpath = os.path.join(
        absolute_path, file_path_row.observed_path
    )
    print("")
    if not os.path.isfile(fullpath):
        print("Is not a file, skipping: " + fullpath)
        return
    print("Importing " + fullpath)
    rows_updated = file_path_row.update_observed_file_state_if_state_is(
        "IMPORTING", "STABLE", conn
    )
    if rows_updated == 0:
        print("File was not stable as expected, skipping import")
        return
    try:
        # Attempt reading the file before updating the database to avoid
        # creating rows for a file we can't read.
        # TODO handle rows in the dataset and access tables with no
        # corresponding data since the import might fail while reading the data
        # anyway
        input_file = None
        for input_file_cls in registered_input_files:
            try:
                print('Tried input reader {}'.format(input_file_cls))
                input_file = input_file_cls(fullpath)
            except Exception as e:
                print('...failed with: ', type(e), e)
            else:
                print('...succeeded...')
                break
        if input_file is None:
            raise UnsupportedFileTypeError

        print("File successfully imported")
    except Exception as e:
        file_path_row.update_observed_file_state("IMPORT_FAILED", conn)
        print("Import failed for " + fullpath)
        # perhaps the exception should be saved to the database
        # print it for now during development
        traceback.print_exc()
