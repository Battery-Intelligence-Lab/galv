# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import os
import unittest
import logging

from .utils import GalvTeamResourceTestCase
from .factories import ScheduleFactory, make_tmp_file

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class ScheduleTests(GalvTeamResourceTestCase):
    stub = 'schedule'
    factory = ScheduleFactory

    def get_edit_kwargs(self):
        return {'schedule_file': make_tmp_file()}

if __name__ == '__main__':
    unittest.main()
