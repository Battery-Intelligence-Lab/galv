# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import os

import json
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
import sys
import logging
import requests
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
from settings import get_setting, get_logfile


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)
# stream_handler = logging.StreamHandler(sys.stdout)
# stream_handler.setLevel(logging.INFO)
# logger.addHandler(stream_handler)
file_handler = logging.FileHandler(get_logfile())
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)


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


def report(
        path: os.PathLike|str,
        content=None,
        file: os.PathLike|str = None,
        error: BaseException = None
):
    try:
        if error is not None:
            data = {'status': 'error', 'error': ";".join(error.args)}
        else:
            data = {'status': 'success', 'content': content}
        data['path'] = path
        if file is not None:
            data['file'] = file
        logger.debug(f"{get_setting('url')}report/; {json.dumps(data)}")
        return requests.post(
            f"{get_setting('url')}report/",
            headers={
                'Authorization': f"Harvester {get_setting('api_key')}"
            },
            json=data
        )
    except BaseException as e:
        logger.error(e)
    return None


def import_file(core_path: str, file_path: str):
    """
        Attempts to import a given file
    """
    full_file_path = os.sep.join([core_path, file_path])
    print("")
    if not os.path.isfile(full_file_path):
        print("Is not a file, skipping: " + full_file_path)
        report(path=core_path, file=file_path, error=FileNotFoundError())
        return
    print("Importing " + full_file_path)
    report(
        path=core_path,
        file=file_path,
        content={
            'content': {
                'task': 'import',
                'status': 'begin'
            }
        }
    )

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
                input_file = input_file_cls(full_file_path)
            except Exception as e:
                print('...failed with: ', type(e), e)
            else:
                print('...succeeded...')
                break
        if input_file is None:
            raise UnsupportedFileTypeError

        print("File successfully imported")
    except Exception as e:
        logger.error(e)
        # report(path=core_path, file=file_path, error=e)
