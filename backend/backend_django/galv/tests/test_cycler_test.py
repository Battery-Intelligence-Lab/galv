# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
import logging

from backend.backend_django.galv.tests.utils import GalvTeamResourceTestCase
from .factories import CyclerTestFactory, CellFactory

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class CyclerTestTests(GalvTeamResourceTestCase):
    stub = 'cyclertest'
    factory = CyclerTestFactory

    def get_edit_kwargs(self):
        cell_subject = CellFactory.create()
        return {'cell_subject': cell_subject.pk}

if __name__ == '__main__':
    unittest.main()
