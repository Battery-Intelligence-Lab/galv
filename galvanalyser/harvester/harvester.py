import os
import sys
import json
import psutil
import psycopg2
from datetime import datetime, timezone
from galvanalyser.database.harvester.harvester_row import HarvesterRow
from galvanalyser.database.harvester.monitored_path_row import MonitoredPathRow
from galvanalyser.database.harvester.observed_file_row import (
    ObservedFileRow,
    ObservedFilePathRow,
)
from galvanalyser.database.experiment.institution_row import InstitutionRow
from galvanalyser.database.experiment.dataset_row import DatasetRow
from galvanalyser.database.experiment.access_row import AccessRow
from galvanalyser.database.experiment.timeseries_data_row import (
    TimeseriesDataRow,
)
from galvanalyser.harvester.input_file import InputFile
from galvanalyser.database.experiment.range_label_row import RangeLabelRow
from galvanalyser.database.experiment.misc_file_data_row import MiscFileDataRow
import galvanalyser.harvester.battery_exceptions as battery_exceptions

import traceback


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
        "institution": "Oxford",
    }
    with open(config_template_path, "w") as json_file:
        json.dump(template, json_file, indent=4)


def monitor_path(monitor_path_id, path, monitored_for, conn):
    print("Examining " + path + " for users " + str(monitored_for))
    try:
        current_files = os.listdir(path)
    except FileNotFoundError:
        print("ERROR: Requested path not found on this machine: " + path)
        return
    for file_path in current_files:
        full_file_path = os.path.join(path, file_path)
        print("Found " + full_file_path)
        current_observation = ObservedFileRow(
            monitor_path_id,
            file_path,
            os.path.getsize(full_file_path),
            datetime.now(timezone.utc),
        )
        database_observation = ObservedFileRow.select_from_id_and_path(
            monitor_path_id, file_path, conn
        )
        if database_observation is None:
            print("Found a new file " + file_path)
            current_observation.insert(conn)
        else:
            print(current_observation.last_observed_time)
            print(database_observation.last_observed_time)
            if (
                database_observation.file_state == "STABLE"
                and current_observation.last_observed_size
                != database_observation.last_observed_size
            ):
                print(
                    "File has changed size since last it was checked, "
                    "marking as unstable"
                )
                current_observation.file_state = "UNSTABLE"
                current_observation.insert(conn)
                continue
            elif (
                database_observation.file_state == "IMPORTED"
                and current_observation.last_observed_size
                > database_observation.last_observed_size
            ):
                print(
                    "Imported file has changed size since last it was "
                    "checked, marking as growing"
                )
                current_observation.file_state = "GROWING"
                current_observation.insert(conn)
                continue
            elif (
                database_observation.file_state != "UNSTABLE"
                or database_observation.file_state != "GROWING"
            ):
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
    print("Done monitoring paths")


def import_file(file_path_row, institution_id, harvester_name, conn):
    """
        Attempts to import a given file
    """
    fullpath = os.path.join(
        file_path_row.monitored_path, file_path_row.observed_path
    )
    print("")
    if not os.path.isfile(fullpath):
        print("Is not file, skipping: " + fullpath)
        return
    print("Importing " + fullpath)
    file_path_row.update_observed_file_state("IMPORTING", conn)
    try:
        # Attempt reading the file before updating the database to avoid
        # creating rows for a file we can't read.
        # TODO handle rows in the dataset and access tables with no
        # corresponding data since the import might fail while reading the data
        # anyway
        input_file = InputFile(fullpath)
        # use a transaction to avoid generating dataset rows if import fails
        conn.autocommit = False
        with conn:
            # Check if this dataset is already in the db
            dataset_row = DatasetRow.select_from_name_date_and_institution_id(
                name=input_file.metadata["Dataset Name"],
                date=input_file.metadata["Date of Test"],
                institution_id=institution_id,
                conn=conn,
            )
            is_new_dataset = dataset_row is None
            last_data = None
            if is_new_dataset:
                dataset_row = DatasetRow(
                    name=input_file.metadata["Dataset Name"],
                    date=input_file.metadata["Date of Test"],
                    institution_id=institution_id,
                    dataset_type=input_file.metadata["Machine Type"],
                )
                dataset_row.insert(conn)
                print("Added dataset id " + str(dataset_row.id))
            else:
                print("This dataset is already in the database")
                last_data = TimeseriesDataRow.select_latest_by_dataset_id(
                    dataset_row.id, conn
                )
            dataset_id = dataset_row.id
            for user in file_path_row.monitored_for:
                print("  Allowing access to " + user)
                access_row = AccessRow(dataset_id=dataset_id, user_name=user)
                access_row.insert(conn)
            input_file.metadata["dataset_id"] = dataset_id
            new_data = True
            if is_new_dataset:
                print("Inserting Data")
                TimeseriesDataRow.insert_input_file(
                    input_file, dataset_id, conn
                )
                RangeLabelRow(
                    dataset_id,
                    "all",
                    harvester_name,
                    int(input_file.metadata["first_sample_no"]),
                    int(input_file.metadata["last_sample_no"]) + 1,
                ).insert(conn)
                for label, sample_range in input_file.get_data_labels():
                    print("inserting {}".format(label))
                    RangeLabelRow(
                        dataset_id,
                        label,
                        harvester_name,
                        sample_range[0],
                        sample_range[1],
                    ).insert(conn)
            elif (
                TimeseriesDataRow.select_one_from_dataset_id_and_sample_no(
                    dataset_id, input_file.metadata["first_sample_no"], conn
                )
                is None
                and TimeseriesDataRow.select_one_from_dataset_id_and_sample_no(
                    dataset_id, input_file.metadata["last_sample_no"], conn
                )
                is None
            ):
                # This is more data for an existing experiment
                print("Inserting Additional Data")
                TimeseriesDataRow.insert_input_file(
                    input_file, dataset_id, conn
                )
                # TODO handle inserting metadata when extending a dataset
            else:
                print("Dataset already in database")
                new_data = False
            if new_data and "misc_file_data" in input_file.metadata:
                print("Storing misc file metadata")
                for key, value in input_file.metadata[
                    "misc_file_data"
                ].items():
                    (json_dict, binary_blob) = value
                    mfdr = MiscFileDataRow(
                        dataset_id,
                        int(input_file.metadata["first_sample_no"]),
                        int(input_file.metadata["last_sample_no"]) + 1,
                        key,
                        json_dict,
                        binary_blob,
                    )
                    mfdr.insert(conn)
            file_path_row.update_observed_file_state("IMPORTED", conn)
            print("File successfully imported")
    except Exception as e:
        conn.autocommit = True
        file_path_row.update_observed_file_state("IMPORT_FAILED", conn)
        print("Import failed for " + fullpath)
        # perhaps the exception should be saved to the database
        # print it for now during development
        if isinstance(e, battery_exceptions.UnsupportedFileTypeError):
            print("File format not supported")
        else:
            traceback.print_exc()
    finally:
        conn.autocommit = True


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
            my_harvester_id = HarvesterRow.select_from_machine_id(
                config["machine_id"], conn
            ).id
        except AttributeError:
            print(
                "Error: Could not find a harvester id for a machine called "
                + config["machine_id"]
                + " in the harvester database"
            )
            sys.exit(1)
        try:
            institution_id = InstitutionRow.select_from_name(
                config["institution"], conn
            ).id
        except AttributeError:
            print(
                "Error: Could not find a institution id for an institution "
                "called "
                + config["institution"]
                + " in the experiment database"
            )
            sys.exit(1)
        monitored_paths_rows = MonitoredPathRow.select_from_harvester_id(
            my_harvester_id, conn
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
        stable_observed_file_path_rows = ObservedFilePathRow.select_from_harvester_id_with_state(
            my_harvester_id, "STABLE", conn
        )
        for stable_observed_file_path_row in stable_observed_file_path_rows:
            # import the file
            import_file(
                stable_observed_file_path_row,
                institution_id,
                config["machine_id"],
                conn,
            )

    finally:
        conn.close()


if __name__ == "__main__":
    main(sys.argv)
