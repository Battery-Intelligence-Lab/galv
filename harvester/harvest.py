import os.path
import sys
import time
import requests
import logging
import json
from settings import get_logfile, get_setting, get_settings, get_settings_file
from parse.harvester import import_file


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)
# stream_handler = logging.StreamHandler(sys.stdout)
# stream_handler.setLevel(logging.INFO)
# logger.addHandler(stream_handler)
file_handler = logging.FileHandler(get_logfile())
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)


def split_path(core_path: os.PathLike|str, path: os.PathLike|str) -> (os.PathLike, os.PathLike):
    """
    Split a path into the base path property and the rest
    """
    path = os.path.abspath(path)
    core_path_abs = os.path.abspath(core_path)
    return core_path, os.path.relpath(path, core_path_abs)


def report_harvest_result(
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


def update_config():
    logger.info("Updating configuration from API")
    try:
        url = get_setting('url')
        key = get_setting('api_key')
        result = requests.get(f"{url}config/", headers={'Authorization': f"Harvester {key}"})
        if result.status_code == 200:
            dirty = False
            new = result.json()
            old = get_settings()
            if old is None:
                old = {}
            all_keys = [*new.keys(), *old.keys()]
            for key in all_keys:
                if key in old.keys() and key in new.keys():
                    if json.dumps(old[key]) == json.dumps(new[key]):
                        continue
                    logger.info(f"Updating value for setting '{key}'")
                    logger.info(f"Old value: {json.dumps(old[key])}")
                    logger.info(f"New value: {json.dumps(new[key])}")
                    dirty = True
                if key in old.keys():
                    logger.info(f"Updating value for setting '{key}'")
                    logger.info(f"Old value: {json.dumps(old[key])}")
                    logger.info(f"New value: [not set]")
                    dirty = True
                if key in new.keys():
                    logger.info(f"Updating value for setting '{key}'")
                    logger.info(f"Old value: [not set]")
                    logger.info(f"New value: {json.dumps(new[key])}")
                    dirty = True

            if dirty:
                with open(get_settings_file(), 'w') as f:
                    json.dump(result.json(), f)
        else:
            logger.error(f"Unable to fetch {url}config/ -- received HTTP {result.status_code}")
    except BaseException as e:
        logger.error(e)


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
                try:
                    full_path = os.path.join(dir_path, filename)
                    core_path, file_path = split_path(path, full_path)
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
                        if status == 'STABLE':
                            logger.info(f"Parsing STABLE file {file_path}")
                            result = import_file(core_path, file_path)
                            report_harvest_result(path=core_path, file=file_path, content=result)
                except BaseException as e:
                    logger.error(e)
                    report_harvest_result(path=path, file=full_path, error=e)
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


if __name__ == "main":
    run()
