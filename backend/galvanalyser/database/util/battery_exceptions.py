# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

class UnsupportedFileTypeError(Exception):
    """
        Exception indicating the file is unsupported
    """

    pass


class InvalidDataInFileError(Exception):
    """
        Exception indicating the file has invalid data
    """

    pass


class EmptyFileError(Exception):
    """
        Exception indicating the file has no data
    """

    pass


class DataGenerationError(Exception):
    """
        Exception indicating the failure to generate some columns
    """

    pass


class InsertError(Exception):
    """
        Exception indicating the failure to insert data
    """

    pass
