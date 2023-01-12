import os
import json
import requests
from .settings import get_setting, get_settings, get_settings_file, get_logger

logger = get_logger(__file__)


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
