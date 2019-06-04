#!/usr/bin/env python

# =========================== MRG Copyright Header ===========================
#
# Copyright (c) 2003-2019 University of Oxford. All rights reserved.
# Authors: Mobile Robotics Group, University of Oxford
#          http://mrg.robots.ox.ac.uk
#
# This file is the property of the University of Oxford.
# Redistribution and use in source and binary forms, with or without
# modification, is not permitted without an explicit licensing agreement
# (research or commercial). No warranty, explicit or implicit, provided.
#
# =========================== MRG Copyright Header ===========================
#
# @author Luke Pitt.
#

import galvanalyser.harvester.battery_exceptions as battery_exceptions
import galvanalyser.harvester.maccor_functions as maccor_functions
from itertools import accumulate
import traceback

# see https://gist.github.com/jsheedy/ed81cdf18190183b3b7d
# https://stackoverflow.com/a/30721460


def load_metadata(file_type, file_path):
    """
        Reads metadata contained in the file and
        Identifies which columns are present in the file and which have data
    """
    if "MACCOR" in file_type:
        if "EXCEL" in file_type:
            return maccor_functions.load_metadata_maccor_excel(file_path)
        else:
            return maccor_functions.load_metadata_maccor_text(
                file_type, file_path
            )
    else:
        raise battery_exceptions.UnsupportedFileTypeError


def identify_file(file_path):
    """
        Returns a string identifying the type of the input file
    """
    if file_path.endswith(".xls"):
        return "EXCEL-MACCOR"
    elif file_path.endswith(".csv"):
        return "CSV-MACCOR"
    elif file_path.endswith(".txt"):
        return "TSV-MACCOR"
    else:
        raise battery_exceptions.UnsupportedFileTypeError


def get_default_sample_time_setep(file_type):
    # TODO handle other file types
    # TODO do something better here
    if "MACCOR" in file_type:
        return 1.0 / 60.0
    else:
        raise battery_exceptions.UnsupportedFileTypeError


class InputFile:
    """
        A class for handling input files
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.type = identify_file(file_path)
        self.metadata, self.columns_with_data = load_metadata(
            self.type, file_path
        )
        # there should be some map of loaded data, not sure whether to use file cols or standard cols
        self.generated_columns = {}

    def get_test_start_date(self):
        # TODO look check file type, ask specific implementation for metadata value
        return self.metadata["Date of Test"]

    def generate_missing_columns(self, possibly_missing_colums, data):
        """
            Recursively generate missing columns.
            Some columns depend on the existence of others, this method
            generates the columns in order of fewest dependencies to most
            generating dependant columns first. Each recursion generates at
            most one column until all required columns are generated.
        """
        print("generate_missing_columns")
        print("possibly_missing_colums: " + str(possibly_missing_colums))
        missing_colums = [
            col
            for col in possibly_missing_colums
            if col not in self.generated_columns.keys()
        ]
        print("missing_colums: " + str(missing_colums))
        changes_made = len(missing_colums) != len(possibly_missing_colums)
        print("changes_made: " + str(changes_made))
        num_rows = len(next(iter(data.values())))
        print("num_rows: " + str(num_rows))
        if (
            "experiment_id" in missing_colums
            and "experiment_id" in self.metadata
        ):
            self.generated_columns["experiment_id"] = [
                self.metadata["experiment_id"]
            ] * num_rows
            changes_made = True
            print("Generated missing column experiment_id")
        elif "sample_no" in missing_colums:
            self.generated_columns["sample_no"] = [
                i for i in range(1, num_rows + 1)
            ]
            changes_made = True
            print("Generated missing column sample_no")
        elif "capacity" in missing_colums:
            print("Generating missing column capacity")
            print("len of data['amps'] is : " + str(len(data["amps"])))
            # capacity = [0] * num_rows
            # total = 0.0
            # for index, value in enumerate(data["amps"]):
            #    total += value
            #    capacity[index] = total
            # self.generated_columns["capacity"] = capacity
            self.generated_columns["capacity"] = list(
                accumulate(map(float, data["amps"]))
            )
            changes_made = True
            print("Generated missing column capacity")
        elif "power" in missing_colums:
            power = [
                float(data["volts"][i]) * float(data["amps"][i])
                for i in range(num_rows)
            ]
            self.generated_columns["power"] = power
            changes_made = True
            print("Generated missing column power")

        print("changes_made 2: " + str(changes_made))
        if changes_made:
            self.generate_missing_columns(missing_colums, data)
        elif len(missing_colums) > 0:
            print("Error missing these columns and unable to generate them:")
            print(missing_colums)
            raise battery_exceptions.DataGenerationError

    def get_generatable_columns(self):
        """
            Returns a list of columns that can be generated
        """
        return ["Cyc#", "State", "DPt Time", "Step", "StepTime", "Power"]

    def complete_columns(self, required_columns, file_cols_to_data_generator):
        """
            Generates missing columns, returns generator of lists that match
            required_columns
        """
        rec_col_set = set(required_columns)
        capacity_total = 0.0
        for row_no, file_data_row in enumerate(file_cols_to_data_generator):
            missing_colums = rec_col_set - set(file_data_row.keys())
            if (
                "experiment_id" in missing_colums
                and "experiment_id" in self.metadata
            ):
                file_data_row["experiment_id"] = self.metadata["experiment_id"]
            if "sample_no" in missing_colums:
                file_data_row["sample_no"] = row_no
            if "temperature" in missing_colums:
                file_data_row["temperature"] = None
            if "capacity" in missing_colums:
                capacity_total += float(file_data_row["amps"])
                file_data_row["capacity"] = capacity_total
            if "power" in missing_colums:
                file_data_row["power"] = float(file_data_row["volts"]) * float(
                    file_data_row["amps"]
                )
                # file_data_row[col_name] if col_name in file_data_row else None
            yield [file_data_row[col_name] for col_name in required_columns]

    def get_data_with_standard_colums(
        self, required_columns, standard_cols_to_file_cols={}
    ):
        """
            Given a map of standard columns to file columns; return a map
            containing the given standard columns as keys with lists of data
            as values.
        """
        print("get_data_with_standard_colums")
        print("Required columns: " + str(required_columns))
        output_columns = set(required_columns) | set(
            standard_cols_to_file_cols.keys()
        )
        print("output_columns: " + str(output_columns))
        # first determine
        file_col_to_std_col = {}
        print("Full type is " + str(self.type))
        # Get the column mappings the file type knows about
        if "MACCOR" in self.type:
            print("Type is MACCOR")
            file_col_to_std_col = (
                maccor_functions.get_maccor_column_to_standard_column_mapping()
            )
        print("file_col_to_std_col 1: " + str(file_col_to_std_col))
        # extend those mappings with any custom ones provided
        file_col_to_std_col.update(
            {
                value: key
                for key, value in standard_cols_to_file_cols.items()
                if value is not None
            }
        )
        print("file_col_to_std_col 2: " + str(file_col_to_std_col))
        #        file_col_to_std_col.update({standard_cols_to_file_cols[key]: key for
        #                                    key in standard_cols_to_file_cols.keys()
        #                                    if standard_cols_to_file_cols[key]
        #                                    is not None})

        desired_file_cols_to_std_cols = {
            key: value
            for key, value in file_col_to_std_col.items()
            if value in required_columns
        }
        file_cols_to_data_generator = self.get_desired_data_if_present(
            desired_file_cols_to_std_cols
        )
        # pass file_cols_to_data_generator to generate missing column

        return self.complete_columns(
            required_columns, file_cols_to_data_generator
        )

    def get_desired_data_if_present(self, desired_file_cols_to_std_cols={}):
        """
            now a generator
            Given a map of file_columns to standard_columns,
            get the file columns that are present,
            return a map of standard_colums to lists of data
        """
        print("get_desired_data_if_present")
        print(
            "desired_file_cols_to_std_cols: "
            + str(desired_file_cols_to_std_cols)
        )
        # first find which desired columns are available
        available_columns = {
            key
            for key, value in self.columns_with_data.items()
            if value["has_data"]
        }
        available_desired_columns = available_columns & set(
            desired_file_cols_to_std_cols.keys()
        )
        print("available_desired_columns: " + str(available_desired_columns))
        # now load the available data
        # we need to pass whether the column is numeric to these
        if "MACCOR" in self.type:
            if "EXCEL" in self.type:
                return maccor_functions.load_data_maccor_excel(
                    self.file_path,
                    available_desired_columns,
                    desired_file_cols_to_std_cols,
                )
            else:
                return maccor_functions.load_data_maccor_text(
                    self.type,
                    self.file_path,
                    available_desired_columns,
                    desired_file_cols_to_std_cols,
                )
        else:
            raise battery_exceptions.UnsupportedFileTypeError

    def get_data_row_generator(self, required_column_names):
        # given list of columns, map file columns to desired columns
        # load available columns
        # generate missing columns
        # store data values in map of standard columns to lists of data values
        # generate list of iterators of data columns in order of input list
        # yield a single line of tab separated quoted values
        try:
            for row in self.get_data_with_standard_colums(
                required_column_names
            ):
                yield "\t".join(map(str, row))
            # while True:
            #    yield "\t".join(
            #        [(str(next(iterator))) for iterator in iterators]
            #    )
        # except StopIteration:
        #    return
        except:
            traceback.print_exc()
            raise

    def get_data_generating_missing_columns(self, required_column_names):
        """
            Generator that returns lists with one entry per requested column
            Generates columns if needed
        """
        available_file_columns = [
            col
            for col in required_column_names
            if col in self.columns_with_data
        ]
