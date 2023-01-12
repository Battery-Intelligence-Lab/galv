import json
import os
import pathlib
import logging

logging.basicConfig(level=logging.INFO)


def get_settings_file() -> pathlib.Path:
    return pathlib.Path(os.getenv('SETTINGS_FILE', "/harvester_files/.harvester.json"))


def get_logfile() -> pathlib.Path:
    return pathlib.Path(os.getenv('LOG_FILE', "/harvester_files/harvester.log"))


def get_settings():
    try:
        with open(get_settings_file(), 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding json file {f.name}", e)
                f.seek(0)
                print(f.readlines())
    except FileNotFoundError:
        print(f'No config file at {get_settings_file()}')
    return None


def get_setting(*args):
    settings = get_settings()
    if not settings:
        if len(args) == 1:
            return None
        return [None for _ in args]
    if len(args) == 1:
        return settings.get(args[0])
    return [settings.get(arg) for arg in args]


def get_standard_units():
    return {u['name']: u['id'] for u in get_setting('standard_units')}


def get_standard_columns():
    return {u['name']: u['id'] for u in get_setting('standard_columns')}


def get_logger(name):
    logger = logging.getLogger(name)
    # stream_handler = logging.StreamHandler(sys.stdout)
    # stream_handler.setLevel(logging.INFO)
    # logger.addHandler(stream_handler)
    file_handler = logging.FileHandler(get_logfile())
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logger
