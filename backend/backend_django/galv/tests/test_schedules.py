# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import os
import unittest
import logging

from django.core.files.uploadedfile import SimpleUploadedFile

from .utils import GalvTeamResourceTestCase
from .factories import ScheduleFactory

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class ScheduleTests(GalvTeamResourceTestCase):
    stub = 'schedule'
    factory = ScheduleFactory

    def get_edit_kwargs(self):
        file = self.factory.create().schedule_file
        with open(str(file), 'rb') as f:
            content = SimpleUploadedFile(str(file), f.read(), content_type="xml")
        return {'schedule_file': content}

if __name__ == '__main__':
    unittest.main()
