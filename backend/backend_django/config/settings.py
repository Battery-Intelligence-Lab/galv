# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import os

if 'DJANGO_SETTINGS' in os.environ and os.environ['DJANGO_SETTINGS'] == "dev":
    from .settings_dev import *
else:
    from .settings_prod import *
