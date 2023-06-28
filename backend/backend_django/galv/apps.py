# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

from django.apps import AppConfig


class GalvConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'galv'
