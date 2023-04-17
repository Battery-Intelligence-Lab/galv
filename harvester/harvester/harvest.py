# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import datetime
import json
import os
import time

import dateutil
import sys
from .parse.exceptions import UnsupportedFileTypeError

from .parse.ivium_input_file import IviumInputFile
from .parse.biologic_input_file import BiologicMprInputFile
from .parse.maccor_input_file import (
    MaccorInputFile,
    MaccorExcelInputFile,
    MaccorRawInputFile,
)

from .settings import get_logger, get_setting, get_standard_units, get_standard_columns
from .api import report_harvest_result

logger = get_logger(__file__)


registered_input_files = [
    BiologicMprInputFile,
    IviumInputFile,
    MaccorInputFile,
    MaccorExcelInputFile,
    MaccorRawInputFile,
]


def serialize_datetime(v):
    """
    Recursively search for date[time] classes and convert
    dates to iso format strings and datetimes to timestamps
    """
    if isinstance(v, datetime.datetime):
        return v.timestamp()
    if isinstance(v, datetime.date):
        return v.isoformat()
    if isinstance(v, dict):
        return {k: serialize_datetime(x) for k, x in v.items()}
    if isinstance(v, list):
        return [serialize_datetime(x) for x in v]
    return v


def import_file(core_path: str, file_path: str) -> bool:
    """
        Attempts to import a given file
    """
    default_column_ids = get_standard_columns()
    default_units = get_standard_units()
    max_upload_size = get_setting('max_upload_bytes')
    full_file_path = os.sep.join([core_path, file_path])
    if not os.path.isfile(full_file_path):
        logger.warn(f"{full_file_path} is not a file, skipping")
        report_harvest_result(path=core_path, file=file_path, error=FileNotFoundError())
        return False
    logger.info("Importing " + full_file_path)

    try:
        # Attempt reading the file before updating the database to avoid
        # creating rows for a file we can't read.
        # TODO handle rows in the dataset and access tables with no
        # corresponding data since the import might fail while reading the data
        # anyway
        input_file = None
        for input_file_cls in registered_input_files:
            try:
                logger.debug('Tried input reader {}'.format(input_file_cls))
                input_file = input_file_cls(
                    file_path=full_file_path,
                    standard_units=default_units,
                    standard_columns=default_column_ids
                )
            except Exception as e:
                logger.debug('...failed with: ', type(e), e)
            else:
                logger.debug('...succeeded...')
                break
        if input_file is None:
            raise UnsupportedFileTypeError

        # Send metadata
        core_metadata, extra_metadata = input_file.load_metadata()
        report = report_harvest_result(
            path=core_path,
            file=file_path,
            content={
                'task': 'import',
                'status': 'begin',
                'core_metadata': serialize_datetime(core_metadata),
                'extra_metadata': serialize_datetime(extra_metadata),
                'test_date': serialize_datetime(core_metadata['Date of Test'])
            }
        )
        if report is None:
            logger.error(f"API Error")
            return False
        if not report.ok:
            try:
                logger.error(f"API responded with Error: {report.json()['error']}")
            except BaseException:
                logger.error(f"API Error: {report.status_code}")
            return False
        upload_info = report.json()['upload_info']
        last_uploaded_record = upload_info.get('last_record_number')
        columns = upload_info.get('columns')

        # Figure out column data
        column_data = {}
        if len(columns):
            mapping = {c.get('name'): c.get('id') for c in columns}
            value_map = {c.get('name'): c.get('keymap') for c in columns if len(c.get('keymap'))}
        else:
            mapping = input_file.get_file_column_to_standard_column_mapping()
            value_map = {}
        next_key = 0
        # limit size of requests. 1kb/column is an arbitrary buffer size.
        size = 0
        max_size = max_upload_size
        nth_part = 0
        start_row = last_uploaded_record if last_uploaded_record is not None else 0
        # Find out if there's a Sample number column, otherwise we use the row number
        record_number_column = [k for k, v in mapping.items() if v == default_column_ids['Sample Number']]
        record_number_column = record_number_column[0] if len(record_number_column) else None
        # TODO: is this actually determined correctly? Seems there are actually lots of data columns we miss??
        # Anyway, leaving this as instructed because everyone's happy with it as is.
        columns_with_data = [c for c in input_file.column_info.keys() if input_file.column_info[c].get('has_data')]
        generator = input_file.load_data(input_file.file_path, columns_with_data)
        start = time.process_time()
        new_row = {}
        for i, r in enumerate(generator):
            if int(r.get(record_number_column, i)) <= start_row:
                continue
            # Data are stored up in rows and shipped out when
            # adding the current row would exceed the server data
            # size limit.
            # If sent, sent data are wiped from column_data.
            # New row data are added to column_data below.
            size += sys.getsizeof(json.dumps(new_row))
            if size > max_size:
                if start_row == i:
                    logger.error(f"Row too large to upload {len(r.keys())} columns, size={sys.getsizeof(r)}")
                    return False
                logger.info(f"Upload part {nth_part} (rows {start_row}-{i - 1}; {size}bytes)")
                logger.info(f"Read took {time.process_time() - start}")
                nth_part += 1
                start_row = i
                report = report_harvest_result(path=core_path, file=file_path, content={
                    'task': 'import',
                    'status': 'in_progress',
                    'data': [v for v in column_data.values()],
                    'test_date': serialize_datetime(core_metadata['Date of Test'])
                })
                if report is None:
                    logger.error(f"API Error")
                    return False
                if not report.ok:
                    try:
                        logger.error(f"API responded with Error: {report.json()['error']}")
                    except BaseException:
                        logger.error(f"API Error: {report.status_code}")
                    return False
                for k in column_data.keys():
                    column_data[k]['values'] = {}
                start = time.process_time()
                size = 0

            if i > 0:
                for k, v in new_row.items():
                    column_data[k]['values'][record_number] = v

            record_number = int(r.get(record_number_column, i))
            new_row = {}

            for k, v in r.items():
                if k == record_number_column:
                    continue
                if k in column_data:
                    # Numeric data are stored directly
                    try:
                        new_row[k] = int(v)
                    except ValueError:
                        try:
                            new_row[k] = float(v)
                        # Timestamps are stored using float conversion
                        except ValueError:
                            try:
                                new_row[k] = dateutil.parser.parse(v).timestamp()
                            # Strings are mapped to integer values using a value map which is also sent to the database
                            except ValueError:
                                if 'value_map' in column_data[k] and v in column_data[k]['value_map']:
                                    new_row[k] = column_data[k]['value_map'][v]
                                else:
                                    if 'value_map' in column_data[k]:
                                        column_data[k]['value_map'][v] = next_key
                                    else:
                                        column_data[k]['value_map'] = {v: next_key}
                                    new_row[k] = next_key
                                    next_key += 1
                else:
                    column_data[k] = {}
                    if k in mapping:
                        column_data[k]['column_id'] = mapping[k]
                    else:
                        column_data[k]['column_name'] = k
                        if 'unit' in input_file.column_info[k]:
                            column_data[k]['unit_symbol'] = input_file.column_info[k].get('unit')
                        else:
                            column_data[k]['unit_id'] = default_units['Unitless']
                    if k in value_map:
                        column_data[k]['value_map'] = value_map[k]
                    column_data[k]['values'] = {}

        # Send data
        report = report_harvest_result(path=core_path, file=file_path, content={
            'task': 'import',
            'status': 'in_progress',
            'data': [v for v in column_data.values()],
            'test_date': serialize_datetime(core_metadata['Date of Test'])
        })
        if report is None:
            logger.error(f"API Error")
            return False
        if not report.ok:
            try:
                logger.error(f"API responded with Error: {report.json()['error']}")
            except BaseException:
                logger.error(f"API Error: {report.status_code}")
            return False

        logger.info("File successfully imported")
    except Exception as e:
        logger.error(e)
        report_harvest_result(path=core_path, file=file_path, error=e)
        return False
    return True
