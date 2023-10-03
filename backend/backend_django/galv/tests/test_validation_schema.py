# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
import logging

from .utils import GalvTeamResourceTestCase
from .factories import ValidationSchemaFactory, to_validation_schema

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class ValidationSchemaTests(GalvTeamResourceTestCase):
    stub = 'validationschema'
    factory = ValidationSchemaFactory
    edit_kwargs = {'schema': to_validation_schema({'type': 'object'})}

if __name__ == '__main__':
    unittest.main()
