# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
import logging

from .utils import  GalvTeamResourceTestCase
from .factories import CellFamilyFactory

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class CellFamilyTests(GalvTeamResourceTestCase):
    stub = 'cellfamily'
    factory = CellFamilyFactory
    edit_kwargs = {'form_factor': 'test'}

if __name__ == '__main__':
    unittest.main()
