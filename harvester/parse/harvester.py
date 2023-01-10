# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import os

import json
import typing

import psutil

from .database.util.battery_exceptions import UnsupportedFileTypeError
from .database.util.iter_file import IteratorFile
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

from typing import TypedDict

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

RECORD_NO_COLUMN_ID = 0
UNIT_UNITLESS = 1


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
            'task': 'import',
            'status': 'begin'
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

        # TODO: Query server payload size limit
        query_max_size = 2 * 1_000_000  # approx 2MB
        # Figure out column data
        column_data = {}
        mapping = input_file.get_file_column_to_standard_column_mapping()
        record_number_column = [k for k, v in mapping.items() if v == RECORD_NO_COLUMN_ID]
        record_number_column = record_number_column[0] if len(record_number_column) else None
        generator = input_file.load_data(input_file.file_path, input_file.column_info.keys())
        for i, r in enumerate(generator):
            record_number = int(r.get(record_number_column, i))
            for k, v in r.items():
                if k == record_number_column:
                    continue
                if k in column_data:
                    column_data[k]['values'][record_number] = v
                else:
                    column_data[k] = {}
                    if k in mapping:
                        column_data[k]['column_id'] = mapping[k]
                    else:
                        column_data[k]['column_name'] = k
                        if 'unit' in input_file.column_info[k]:
                            column_data[k]['unit_symbol'] = input_file.column_info[k].get('unit')
                        else:
                            column_data[k]['unit_id'] = UNIT_UNITLESS
                    column_data[k]['values'] = {}

        # TODO: Resume/append where record already exists

        # Send data
        report(path=core_path, file=file_path, content={
            'task': 'import',
            'status': 'in_progress',
            'data': [v for v in column_data.values()]
        })

        # Send metadata

        print("File successfully imported")
    except Exception as e:
        logger.error(e)
        # report(path=core_path, file=file_path, error=e)


class DjangoColumn(TypedDict):
    name: str
    unit: typing.Optional[str | int]
    values: list


def column_to_django_column(col) -> DjangoColumn:
    return {
        'name': 'col',
        'unit': None,
        'values': []
    }
