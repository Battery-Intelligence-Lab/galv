import json
import os
import pathlib


def get_settings_file() -> pathlib.Path:
    return pathlib.Path(os.getenv('SETTINGS_FILE', "/harvester_files/.harvester.json"))


def get_logfile() -> pathlib.Path:
    return pathlib.Path(os.getenv('LOG_FILE', "/harvester_files/harvester.log"))


def get_setting(*args):
    with open(get_settings_file(), 'r') as f:
        try:
            settings = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding json file {f.name}", e)
            f.seek(0)
            print(f.readlines())
            if len(args) == 1:
                return None
            return [None for _ in args]
    if len(args) == 1:
        return settings.get(args[0])
    return [settings.get(arg) for arg in args]
