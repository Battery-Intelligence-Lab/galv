# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
import logging

from .utils import GalvTeamResourceTestCase
from .factories import EquipmentFactory

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class EquipmentTests(GalvTeamResourceTestCase):
    stub = 'equipment'
    factory = EquipmentFactory
    edit_kwargs = {'calibration_date': '1970-01-01'}

if __name__ == '__main__':
    unittest.main()
