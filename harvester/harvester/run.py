# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import os.path
import re
import time

from .parse.exceptions import UnsupportedFileTypeError
from .settings import get_logger, get_setting
from .api import report_harvest_result, update_config
from .harvest import import_file, get_import_file_handler

logger = get_logger(__file__)


def split_path(core_path: os.PathLike|str, path: os.PathLike|str) -> (os.PathLike, os.PathLike):
    """
    Split a path into the base path property and the rest
    """
    path = os.path.abspath(path)
    core_path_abs = os.path.abspath(core_path)
    return core_path, os.path.relpath(path, core_path_abs)


def harvest():
    logger.info("Beginning harvest cycle")
    paths = get_setting('monitored_paths')
    if not paths:
        logger.info("No paths are being monitored.")
        return

    logger.debug(paths)

    for path in paths:
        if path.get('active'):
            harvest_path(path)
        else:
            logger.info(f"Skipping inactive path {path.get('path')} {path.get('regex')}")

def harvest_path(monitored_path: dict):
    path = monitored_path.get('path')
    regex_str = monitored_path.get('regex')
    if regex_str is not None:
        logger.info(f"Harvesting from {path} with regex {regex_str}")
    else:
        logger.info(f"Harvesting from {path}")
    try:
        regex = re.compile(regex_str) if regex_str is not None else None
        for (dir_path, dir_names, filenames) in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dir_path, filename)
                core_path, file_path = split_path(path, full_path)
                if regex is not None and not regex.search(file_path):
                    logger.debug(f"Skipping {file_path} as it does not match regex {regex}")
                    continue
                try:
                    get_import_file_handler(full_path)
                except UnsupportedFileTypeError:
                    logger.debug(f"Skipping unsupported file {file_path}")
                    continue
                try:
                    logger.info(f"Reporting stats for {file_path}")
                    result = report_harvest_result(
                        path=full_path,
                        monitored_path_uuid=monitored_path.get('uuid'),
                        content={
                            'task': 'file_size',
                            'size': os.stat(full_path).st_size
                        }
                    )
                    if result is not None:
                        result = result.json()
                        status = result['state']
                        logger.info(f"Server assigned status '{status}'")
                        if status in ['STABLE', 'RETRY IMPORT']:
                            logger.info(f"Parsing file {file_path}")
                            if import_file(full_path, monitored_path):
                                report_harvest_result(
                                    path=full_path,
                                    monitored_path_uuid=monitored_path.get('uuid'),
                                    content={'task': 'import', 'status': 'complete'}
                                )
                                logger.info(f"Successfully parsed file {file_path}")
                            else:
                                logger.warn(f"FAILED parsing file {file_path}")
                                report_harvest_result(
                                    path=full_path,
                                    monitored_path_uuid=monitored_path.get('uuid'),
                                    content={'task': 'import', 'status': 'failed'}
                                )
                except BaseException as e:
                    logger.error(f"{e.__class__.__name__}: {e}")
                    report_harvest_result(
                        path=full_path,
                        monitored_path_uuid=monitored_path.get('uuid'),
                        error=e
                    )
        logger.info(f"Completed directory walking of {path}")
    except BaseException as e:
        logger.error(f"{e.__class__.__name__}: {e}")
        report_harvest_result(
            monitored_path_uuid=monitored_path.get('uuid'),
            error=e,
            path=path
        )


def run():
    update_config()
    harvest()


def run_cycle():
    sleep_time = 10
    while True:
        try:
            run()
        except BaseException as e:
            logger.error(f"{e.__class__.__name__}: {e}")
        try:
            sleep_time = get_setting('sleep_time')
        except BaseException as e:
            logger.error(f"{e.__class__.__name__}: {e}")
        time.sleep(sleep_time)


if __name__ == "__main__":
    run_cycle()
