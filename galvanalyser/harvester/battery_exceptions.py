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
