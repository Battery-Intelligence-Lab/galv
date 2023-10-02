# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
import logging

from .utils import  GalvTeamResourceTestCase
from .factories import ScheduleFamilyFactory

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class ScheduleFamilyTests(GalvTeamResourceTestCase):
    stub = 'schedulefamily'
    factory = ScheduleFamilyFactory
    edit_kwargs = {'description': 'test'}

if __name__ == '__main__':
    unittest.main()
