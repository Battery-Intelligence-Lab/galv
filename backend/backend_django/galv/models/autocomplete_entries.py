# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
from .utils import AutoCompleteEntry


# Reference models that will be used to suggest autocompletion in the frontend.
# Do not shortcut this with a factory because IDEs will not be able to infer the classes' existence.
class EquipmentTypes(AutoCompleteEntry):
    pass


class EquipmentModels(AutoCompleteEntry):
    pass


class EquipmentManufacturers(AutoCompleteEntry):
    pass


class CellModels(AutoCompleteEntry):
    pass


class CellManufacturers(AutoCompleteEntry):
    pass


class CellChemistries(AutoCompleteEntry):
    pass


class CellFormFactors(AutoCompleteEntry):
    pass


class ScheduleIdentifiers(AutoCompleteEntry):
    pass