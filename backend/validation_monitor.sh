#!/bin/sh
# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

cd backend_django || exit 1

while [ 1 -ne 0 ]; do
  python manage.py validate_against_schemas
  sleep 10
done
