# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

from django.apps import AppConfig


class GalvanalyserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'galvanalyser'
