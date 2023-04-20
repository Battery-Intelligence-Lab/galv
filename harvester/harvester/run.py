# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import os.path
import time
from .settings import get_logger, get_setting
from .api import report_harvest_result, update_config
from .harvest import import_file

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
        harvest_path(path.get('path'))


def harvest_path(path: os.PathLike):
    logger.info(f"Harvesting from {path}")
    try:
        for (dir_path, dir_names, filenames) in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dir_path, filename)
                core_path, file_path = split_path(path, full_path)
                try:
                    logger.info(f"Reporting stats for {file_path}")
                    result = report_harvest_result(
                        path=core_path,
                        file=file_path,
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
                            if import_file(core_path, file_path):
                                report_harvest_result(
                                    path=core_path,
                                    file=file_path,
                                    content={'task': 'import', 'status': 'complete'}
                                )
                                logger.info(f"Successfully parsed file {file_path}")
                            else:
                                logger.warn(f"FAILED parsing file {file_path}")
                                report_harvest_result(
                                    path=path,
                                    file=file_path,
                                    content={'task': 'import', 'status': 'failed'}
                                )
                except BaseException as e:
                    logger.error(e)
                    report_harvest_result(path=path, file=file_path, error=e)
        logger.info(f"Completed directory walking of {path}")
    except BaseException as e:
        logger.error(e)
        report_harvest_result(path=path, error=e)


def run():
    update_config()
    harvest()


def run_cycle():
    while True:
        try:
            run()
            sleep_time = get_setting('sleep_time')
            if sleep_time is None:
                sleep_time = 10
            time.sleep(sleep_time)
        except BaseException as e:
            logger.error(e)


if __name__ == "__main__":
    run_cycle()
