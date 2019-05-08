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

    def generate_missing_columns(self, missing_colums, data):
        """
            Recursively generate missing columns.
            Some columns depend on the existence of others, this method
            generates the columns in order of fewest dependencies to most
            generating dependant columns first. Each recursion generates at
            most one column until all required columns are generated.
        """
        changes_made = False
        num_rows = len(data[data.keys()[0]])
        
        if 'Cyc#' in missing_colums:
            data['Cyc#'] = [0] * num_rows
            self.generated_columns['Cyc#'] = data['Cyc#']
            changes_made = True
        elif 'State' in missing_colums:
            data['State'] = ['R'] * num_rows
            self.generated_columns['State#'] = data['State#']
            changes_made = True
        elif 'DPt Time' in missing_colums:
            # get Date of Test: from metadata
            start_date = self.get_test_start_date()
            time_step = get_default_sample_time_setep(self.file_path)
            dpt_times = []
            for i in range(num_rows):
                dpt_times.append(start_date.add(seconds=(i*time_step)))
            self.generated_columns['DPt Time'] = dpt_times
            data['DPt Time'] = dpt_times
            changes_made = True
        elif 'Step' in missing_colums:
            steps = []
            state = ''
            step = 0
            states = data['State']
            for i in range(num_rows):
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
            for i in range(num_rows):
                step_i = steps[i]
                if step_i != prev_step:
                    prev_step = step_i
                    step_start = i
                step_time.append((i - step_start) * time_step)
            self.generated_columns['StepTime'] = step_time
            data['StepTime'] = step_time
            changes_made = True
        elif 'Power' in missing_colums:
            power = [data['Volts'][i] * data['Amps'][i] for i in range(num_rows)]
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


    def get_data_with_standard_colums(self, standard_cols_to_file_cols):
        """
            Given a map of standard columns to file columns; return a map
            containing the given standard columns as keys with lists of data
            as values.
        """
        output_columns = (set(get_required_columns().keys()) +
                          set(standard_cols_to_file_cols.keys()))
        # first determine 
        file_col_to_std_col = {}
        if 'MACCOR' in self.type:
            file_col_to_std_col = maccor_functions.get_maccor_column_to_standard_column_mapping()
        file_col_to_std_col.update({value: key for key, value in
                                    standard_cols_to_file_cols.items()
                                    if value is not None})
#        file_col_to_std_col.update({standard_cols_to_file_cols[key]: key for
#                                    key in standard_cols_to_file_cols.keys()
#                                    if standard_cols_to_file_cols[key]
#                                    is not None})
        file_cols_to_data = self.get_desired_data_if_present(file_col_to_std_col)

         # remap to standard colums : data
        standard_cols_to_data = {file_col_to_std_col[key]: value for
                                 key, value in file_cols_to_data.items()}
        # find the missing columns
        missing_std_cols = {col for col in output_columns if col not in 
                            standard_cols_to_data.keys()}
        # generate the missing columns
        self.generate_missing_columns(missing_std_cols, standard_cols_to_data)
        for missing_col in missing_std_cols:
            standard_cols_to_data[missing_col] = self.generated_columns[missing_col]
        return standard_cols_to_data
        

    def get_desired_data_if_present(self, desired_file_cols_to_std_cols={}):
        """
            Given a map of file_columns to standard_columns,
            get the file columns that are present,
            return a map of standard_colums to lists of data
        """
        # first find which desired columns are available
        available_columns = {key for key, value in
                             self.columns_with_data.items() if value}
        available_desired_columns = (available_columns &
                                     set(desired_file_cols_to_std_cols.keys()))
        # now load the available data
        if "MACCOR" in self.type:
            if "EXCEL" in self.type:
                return maccor_functions.load_data_maccor_excel(self.file_path,
                                                               available_desired_columns)
            else:
                return maccor_functions.load_data_maccor_text(self.type,
                                                              self.file_path,
                                                              available_desired_columns)
        else:
            raise battery_exceptions.UnsupportedFileTypeError
       


