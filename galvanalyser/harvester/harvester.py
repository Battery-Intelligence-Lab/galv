import os
import sys
import json
import psutil
import psycopg2
from datetime import datetime, timezone
from galvanalyser.database.harvester.harvesters_row import HarvestersRow
from galvanalyser.database.harvester.monitored_paths_row import (
    MonitoredPathsRow,
)
from galvanalyser.database.harvester.observed_files_row import (
    ObservedFilesRow,
    ObservedFilePathRow,
)
from galvanalyser.database.experiment.experiments_row import ExperimentsRow
from galvanalyser.database.experiment.access_row import AccessRow
from galvanalyser.database.experiment.data_row import DataRow
from galvanalyser.harvester.input_file import InputFile


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


def load_config(config_file_path):
    with open(config_file_path, "r") as json_file:
        return json.load(json_file)


def write_config_template(config_template_path):
    template = {
        "database_username": "harvester_user",
        "database_password": "password",
        "database_host": "127.0.0.1",
        "database_port": 5432,
        "database_name": "galvanalyser",
        "machine_id": "my_machine_01",
    }
    with open(config_template_path, "w") as json_file:
        json.dump(template, json_file, indent=4)


def monitor_path(monitor_path_id, path, monitored_for, conn):
    print("Examining " + path + " for users " + str(monitored_for))
    current_files = os.listdir(path)
    for file_path in current_files:
        full_file_path = os.path.join(path, file_path)
        print("Found " + full_file_path)
        current_observation = ObservedFilesRow(
            monitor_path_id,
            file_path,
            os.path.getsize(full_file_path),
            datetime.now(timezone.utc),
        )
        database_observation = ObservedFilesRow.select_from_id_and_path(
            monitor_path_id, file_path, conn
        )
        if database_observation is None:
            print("Found a new file " + file_path)
            current_observation.insert(conn)
        else:
            print(current_observation.last_observed_time)
            print(database_observation.last_observed_time)
            if database_observation.file_state != "UNSTABLE":
                # This file has already been handled
                print(
                    "File has already been handled. State is currently "
                    + str(database_observation.file_state)
                )
                continue
            elif (
                current_observation.last_observed_size
                != database_observation.last_observed_size
            ):
                # The file is changing, record its size
                print(
                    "File has changed size since last it was checked, skipping"
                )
                current_observation.insert(conn)
            elif has_handle(full_file_path):
                # the file is currently in use, record this update time
                print("File is currently in use, skipping")
                current_observation.insert(conn)
            elif (
                current_observation.last_observed_time
                - database_observation.last_observed_time
            ).total_seconds() > 60:
                # the file hasn't changed in the last minute
                current_observation.file_state = "STABLE"
                current_observation.insert(conn)
            else:
                # The file hasn't changed this time, but it hasn't been over a
                # minute since we last checked
                # We don't update the database because we don't want to change
                # the timestamp of our last observation and nothing else has
                # changed
                print("Waiting for file to become stable")
                pass
    print("Done monitoring paths")


def import_file(file_path_row, conn):
    """
        Attempts to import a given file
    """
    fullpath = os.path.join(
        file_path_row.monitored_path, file_path_row.observed_path
    )
    print("Importing " + fullpath)
    file_path_row.update_observed_file_state("IMPORTING", conn)
    try:
        input_file = InputFile(fullpath)
        experiment_row = ExperimentsRow(
            name=input_file.metadata["Experiment Name"],
            date=input_file.metadata["Date of Test"],
            experiment_type=input_file.metadata["Machine Type"],
        )
        experiment_row.insert(conn)
        print("Added experiment id " + str(experiment_row.id))
        for user in file_path_row.monitored_for:
            print("  Allowing access to " + user)
            access_row = AccessRow(
                experiment_id=experiment_row.id, user_name=user
            )
            access_row.insert(conn)
        print("Inserting Data")
        DataRow.insert_input_file(input_file, conn)
        file_path_row.update_observed_file_state("IMPORTED", conn)
        print("File successfully imported")
    except:
        file_path_row.update_observed_file_state("IMPORT_FAILED", conn)
        print("Import failed for " + fullpath)


def main(argv):
    config = load_config("./config/harvester-config.json")
    print(config)
    try:
        conn = psycopg2.connect(
            host=config["database_host"],
            port=config["database_port"],
            database=config["database_name"],
            user=config["database_username"],
            password=config["database_password"],
        )
        conn.autocommit = True

        try:
            my_harvester_id_no = HarvestersRow.select_from_machine_id(
                config["machine_id"], conn
            ).id_no
        except AttributeError:
            print(
                "Error: Could not find a harvester id for a machine called "
                + config["machine_id"]
                + " harvester in the database"
            )
            sys.exit(1)
        monitored_paths_rows = MonitoredPathsRow.select_from_harvester_id(
            my_harvester_id_no, conn
        )
        print(
            config["machine_id"]
            + " is monitoring "
            + str(len(monitored_paths_rows))
            + " directories"
        )
        for monitored_paths_row in monitored_paths_rows:
            monitor_path(
                monitored_paths_row.monitor_path_id,
                monitored_paths_row.path,
                monitored_paths_row.monitored_for,
                conn,
            )
        # files for import
        stable_observed_file_path_rows = ObservedFilePathRow.select_from_harvester_id_no_with_state(
            my_harvester_id_no, "STABLE", conn
        )
        for stable_observed_file_path_row in stable_observed_file_path_rows:
            # import the file
            import_file(stable_observed_file_path_row, conn)

    finally:
        conn.close()


if __name__ == "__main__":
    main(sys.argv)
