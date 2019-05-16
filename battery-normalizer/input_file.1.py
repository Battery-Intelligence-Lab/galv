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

import battery_exceptions
import maccor_functions


def load_metadata(file_type, file_path):
    """
        Reads metadata contained in the file
    """
    if "MACCOR" in file_type:
        if "EXCEL" in file_type:
            return maccor_functions.load_metadata_maccor_excel(file_path)
        else:
            return maccor_functions.load_metadata_maccor_text(file_type,
                                                              file_path)
    else:
        raise battery_exceptions.UnsupportedFileTypeError


def identify_columns(file_type, file_path):
    """
        Identifies which columns are present in the file and which have data
    """
    if "MACCOR" in file_type:
        if "EXCEL" in file_type:
            return maccor_functions.identify_columns_maccor_excel(file_path)
        else:
            return maccor_functions.identify_columns_maccor_text(file_type,
                                                                 file_path)
    else:
        raise battery_exceptions.UnsupportedFileTypeError


def identify_file(file_path):
    """
        Returns a string identifying the type of the input file
    """
    if file_path.endswith('.xls'):
        return "EXCEL-MACCOR"
    elif file_path.endswith('.csv'):
        return "CSV-MACCOR"
    elif file_path.endswith('.txt'):
        return "TSV-MACCOR"
    else:
        raise battery_exceptions.UnsupportedFileTypeError

def get_required_columns_ordered():
    """
        Returns a list of column names in order
    """
    return ['Cyc#', 'Step', 'StepTime', 'Amp-hr', 'Watt-hr', 'Amps', 'Volts',
            'State', 'DPt Time']

def get_required_columns():
    """
        Returns a map of columns required and their types
    """
    return {'Amp-hr': 'double', 'Amps': 'double', 'Cyc#': 'int',
            'DPt Time': 'date', 'Watt-hr': 'double', 'State': 'string',
            'Step': 'int', 'StepTime': 'double', 'Volts': 'double'}


def get_optional_columns():
    """
        Returns a map of columns required and their types
    """
    return {'Capacity': 'double', 'Energy': 'double', 'Power': 'double'}

def get_default_sample_time_setep(file_type):
    if "MACCOR" in file_type:
        return 1.0/60.0
    else:
        raise battery_exceptions.UnsupportedFileTypeError

def format_datetime_american(date_time):
    return date_time.strftime('%m/%d/%Y %I:%M:%S %p')

class InputFile:
    """
        A class for handling input files
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.type = identify_file(file_path)
        self.columns_with_data = identify_columns(self.type, file_path)
        self.metadata = load_metadata(self.type, file_path)
        self.generated_columns = {}

    def write_output_file(self, file_path, data):
        """
            Writes standard data to file
        """
        # get standard columns in order
        columns_to_write = get_required_columns_ordered()
        # add custom columns after in any order
        columns_to_write = columns_to_write + [col for col in data.keys() if
                                                col not in columns_to_write]
        num_rows = len(data[data.keys()[0]])
        with open(file_path, "w") as fout:
            fout.write("Today''s Date\t" + format_datetime_american(self.metadata["Today's Date"])+'\n')
            fout.write("Date of Test:\t" + format_datetime_american(self.metadata["Date of Test"])+'\n')
            fout.write('\t'.join(columns_to_write))
            for i in range(num_rows):
                fout.write('\n' + '\t'.join([str(data[key][i]) for key in
                                              columns_to_write]))

    def get_test_start_date(self):
        # look check file type, ask specific implementation for metadata value
        pass
        return self.metadata['Date of Test:']

    def generate_missing_columns(self, data):
        """
            Recursively generate missing columns.
            Some columns depend on the existence of others, this method
            generates the columns in order of fewest dependencies to most
            generating dependant columns first. Each recursion generates at
            most one column until all required columns are generated.
        """
        required_columns = get_required_columns()
        missing_colums = [ col for col in set(required_columns) if col not in
                           data.keys()]
        changes_made = False
        num_missing_values = len(data[data.keys()[0]])
        
        if 'Cyc#' in missing_colums:
            data['Cyc#'] = [0] * num_missing_values
            self.generated_columns['Cyc#'] = data['Cyc#']
            changes_made = True
        elif 'State' in missing_colums:
            data['State'] = ['R'] * num_missing_values
            self.generated_columns['State#'] = data['State#']
            changes_made = True
        elif 'DPt Time' in missing_colums:
            # get Date of Test: from metadata
            start_date = self.get_test_start_date()
            time_step = get_default_sample_time_setep(self.file_path)
            dpt_times = []
            for i in range(num_missing_values):
                dpt_times.append(start_date.add(seconds=(i*time_step)))
            self.generated_columns['DPt Time'] = dpt_times
            data['DPt Time'] = dpt_times
            changes_made = True
        elif 'Step' in missing_colums:
            steps = []
            state = ''
            step = 0
            states = data['State']
            for i in range(num_missing_values):
                state_i = states[i]
                if state_i != state:
                    state = state_i
                    step = step + 1
                steps.append(step)
            self.generated_columns['Step'] = steps
            data['Step'] = steps
            changes_made = True
        elif 'StepTime' in missing_colums:
            step_start = 0
            prev_step = 0
            step_time = []
            steps = data['Step']
            # calculate timestep from test time if available?
            time_step = get_default_sample_time_setep(self.file_path)
            for i in range(num_missing_values):
                step_i = steps[i]
                if step_i != prev_step:
                    prev_step = step_i
                    step_start = i
                step_time.append((i - step_start) * time_step)
            self.generated_columns['StepTime'] = step_time
            data['StepTime'] = step_time
            changes_made = True
        elif 'Power' in missing_colums:
            power = [data['Volts'][i] * data['Amps'][i] for i in range(num_missing_values)]
            self.generated_columns['Power'] = power
            data['Power'] = power
            changes_made = True

        if changes_made:
            return self.generate_missing_columns(data)
        elif len(missing_colums) > 0:
            print ("Error missing these columns and unable to generate them:")
            print (missing_colums)
            raise battery_exceptions.DataGenerationError
    
    def get_generatable_columns(self):
        """
            Returns a list of columns that can be generated
        """
        return ['Cyc#', 'State', 'DPt Time', 'Step', 'StepTime', 'Power']


    def get_required_and_custom_columns(self, available_std_and_custom_columns):
        """
            Get the requested data and generate requested columns if necessarry
        """
        data = self.get_desired_data_if_present(available_std_and_custom_columns)
        if len(self.generated_columns) == 0:
            self.generate_missing_columns(data)
        else:
            data.update(self.generated_columns)
        return data

    def get_standardized_data(self, customized_columns={}):
        """
            get the data
        """
        pass
        available_std_and_custom_columns = self.get_column_to_standard_column_mapping(
            customized_columns)
        return self.get_required_and_custom_columns(available_std_and_custom_columns)
        

    def get_desired_data_if_present(self, customized_columns={}):
        """
            Given a list of standard column names return a dict with a key
            for each standard column present in the file and a value for each
            key that is a list of data that mapped to that standard column
        """
        available_columns = self.get_column_to_standard_column_mapping(
            customized_columns)
        if "MACCOR" in self.type:
            if "EXCEL" in self.type:
                return maccor_functions.load_data_maccor_excel(self.file_path,
                                                               available_columns)
            else:
                return maccor_functions.load_data_maccor_text(self.type,
                                                              self.file_path,
                                                              available_columns)
        else:
            raise battery_exceptions.UnsupportedFileTypeError

    def get_column_to_standard_column_mapping(self, customized_columns={},
                                              include_missing_columns=False):
        """
            Given a map of file column names to output column names return a
            dict with a key of the column name in the file that maps to the
            standard column name in the value. Only return values where a valid
            mapping exists unless include_missing_columns is True
        """
        # fullmap maps file_column_name to standard_column_name
        fullmap = {}
        if 'MACCOR' in self.type:
            fullmap = maccor_functions.get_maccor_column_to_standard_column_mapping()
        fullmap.update(customized_columns)
        if include_missing_columns:
            return fullmap
        available_columns = {key for key, value in
                             self.columns_with_data.items() if value}
        matching_columns = available_columns & set(fullmap.keys())
        return {file_column_name: fullmap[file_column_name] for
                file_column_name in matching_columns}
