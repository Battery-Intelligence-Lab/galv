import os.path
import sys
import time
import requests
import logging
import json
from settings import get_logfile, get_setting, get_settings_file
from parse.harvester import import_file


logger = logging.getLogger(__file__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler(get_logfile()))


def report_harvest_result(path: str, content=None, file: str = None, error: BaseException = None):
    try:
        if error is not None:
            data = {'status': 'error', 'error': error}
        else:
            data = {'status': 'success', 'content': content}
        data['path'] = path
        if file is not None:
            data['file'] = file
        logger.debug(f"{get_setting('url')}report/; {json.dumps(data)}")
        return requests.post(
            f"{get_setting('url')}report/",
            headers={'Authorization': f"Harvester {get_setting('api_key')}"},
            data=data
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
            for setting, value in result.json().items():
                old_value = get_setting(setting)
                if old_value is None:
                    old = "[not set]"
                else:
                    old = json.dumps(get_setting(setting))
                new = json.dumps(value)
                if new != old:
                    logger.info(f"Updating value for setting '{setting}'")
                    logger.info(f"Old value: {old}")
                    logger.info(f"New value: {new}")
                    dirty = True
            # TODO: handle removed values
            if dirty:
                with open(get_settings_file(), 'w') as f:
                    json.dump(result.json(), f)
        else:
            logger.error(f"Unable to fetch {url}config/ -- received HTTP {result.status_code}")
    except BaseException as e:
        logger.error(e)


def harvest():
    logger.info("Beginning harvest cycle")
    paths = get_setting('watched_paths')
    if not paths:
        logger.info("No paths are being watched.")
        return

    for path in paths:
        harvest_path(path)


def harvest_path(path: str):
    logger.info(f"Harvesting from {path}")
    try:
        for (dirpath, dirnames, filenames) in os.walk(path):
            for filename in filenames:
                logger.info(f"Reporting stats for {filename}")
                result = report_harvest_result(
                    path=path,
                    content={
                        'task': 'file_size',
                        'file': filename,
                        'stat': os.stat(filename)
                    }
                )
                if result is not None:
                    result = result.json()
                    status = result['status']
                    logger.info(f"Server assigned status '{status}'")
                    if status == 'STABLE':
                        logger.info(f"Parsing STABLE file {filename}")
                        import_file(os.sep.join([dirpath, filename]))
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
