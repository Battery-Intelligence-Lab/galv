import json
import psutil


def has_handle(fpath):
    for proc in psutil.process_iter():
        try:
            for item in proc.open_files():
                if fpath == item.path:
                    return True
        except Exception:
            pass

    return False


def load_config(config_file_path):
    with open(config_file_path, 'r') as json_file:
        return json.load(json_file)

def harvester_run():
    config = load_config("harvester-config.json")
    


if __name__ == '__main__':
    pass