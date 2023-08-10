# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import json
import os

import factory
import faker
import django.conf.global_settings
from django.contrib.auth.models import User, Group

from galv.models import EquipmentFamily, Harvester, \
    HarvestError, \
    MonitoredPath, \
    ObservedFile, \
    Cell, \
    CellFamily, \
    Equipment, \
    DataUnit, \
    DataColumnType, \
    DataColumn, \
    TimeseriesRangeLabel, \
    FileState, ScheduleFamily, Schedule, CyclerTest, \
    ScheduleIdentifiers, CellFormFactors, CellChemistries, CellManufacturers, \
    CellModels, EquipmentManufacturers, EquipmentModels, EquipmentTypes, Experiment, \
    ValidationSchema

fake = faker.Faker(django.conf.global_settings.LANGUAGE_CODE)

class EquipmentTypesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EquipmentTypes
    value = factory.Faker('bs')
class EquipmentModelsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EquipmentModels
    value = factory.Faker('catch_phrase')
class EquipmentManufacturersFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EquipmentManufacturers
    value = factory.Faker('company')
class CellModelsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CellModels
    value = factory.Faker('catch_phrase')
class CellManufacturersFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CellManufacturers
    value = factory.Faker('company')
class CellChemistriesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CellChemistries
    value = factory.Faker('catch_phrase')
class CellFormFactorsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CellFormFactors
    value = factory.Faker('bs')
class ScheduleIdentifiersFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ScheduleIdentifiers
    value = factory.Faker('bs')


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Faker('user_name')


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ('name',)
        exclude = ('n',)

    n = factory.Faker('random_int', min=1, max=100000)
    name = factory.LazyAttribute(lambda x: f"group_{x.n}")


class HarvesterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Harvester
        django_get_or_create = ('name',)
        exclude = ('first_name',)

    first_name = fake.unique.first_name()
    name = factory.LazyAttribute(lambda x: f"Harvester {x.first_name}")

    @factory.post_generation
    def groups(obj, *args, **kwargs):
        user_group = GroupFactory.create(name=f"harvester_{obj.uuid}_user_group")
        admin_group = GroupFactory.create(name=f"harvester_{obj.uuid}_admin_group")
        obj.user_group = user_group
        obj.admin_group = admin_group
        obj.save()


class MonitoredPathFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonitoredPath
        django_get_or_create = ('path', 'harvester',)
        exclude = ('p',)

    p = factory.Faker(
            'file_path',
            absolute=False,
            depth=factory.Faker('random_int', min=1, max=10)
        )

    path = factory.LazyAttribute(lambda x: os.path.dirname(x.p))
    regex = ".*"
    harvester = factory.SubFactory(HarvesterFactory)

    @factory.post_generation
    def groups(obj, *args, **kwargs):
        user_group = GroupFactory.create(name=f"path_{obj.uuid}_user_group")
        admin_group = GroupFactory.create(name=f"path_{obj.uuid}_admin_group")
        obj.user_group = user_group
        obj.admin_group = admin_group
        obj.save()


class ObservedFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ObservedFile
        django_get_or_create = ('harvester', 'path')

    path = factory.Faker('file_path')
    harvester = factory.SubFactory(HarvesterFactory)


class CellFamilyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CellFamily

    manufacturer = factory.SubFactory(CellManufacturersFactory)
    model = factory.SubFactory(CellModelsFactory)
    form_factor = factory.SubFactory(CellFormFactorsFactory)
    datasheet = factory.Faker('uri')
    chemistry = factory.SubFactory(CellChemistriesFactory)
    nominal_voltage = factory.Faker('pyfloat', min_value=1.0, max_value=1000000.0)
    nominal_capacity = factory.Faker('pyfloat', min_value=1.0, max_value=1000000.0)
    initial_ac_impedance = factory.Faker('pyfloat', min_value=1.0, max_value=1000000.0)
    initial_dc_resistance = factory.Faker('pyfloat', min_value=1.0, max_value=1000000.0)
    energy_density = factory.Faker('pyfloat', min_value=1.0, max_value=1000000.0)
    power_density = factory.Faker('pyfloat', min_value=1.0, max_value=1000000.0)
    additional_properties = factory.Faker('pydict', value_types=['str', 'int', 'float', 'dict', 'list'])

class CellFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cell

    identifier = factory.Faker('bothify', text='?????-##??#-#?#??-?####-?#???')
    family = factory.SubFactory(CellFamilyFactory)
    additional_properties = factory.Faker('pydict', value_types=['str', 'int', 'float', 'dict', 'list'])


class EquipmentFamilyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EquipmentFamily

    type = factory.SubFactory(EquipmentTypesFactory)
    manufacturer = factory.SubFactory(EquipmentManufacturersFactory)
    model = factory.SubFactory(EquipmentModelsFactory)
    additional_properties = factory.Faker('pydict', value_types=['str', 'int', 'float', 'dict', 'list'])


class EquipmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Equipment

    identifier = factory.Faker('bothify', text='?????-##??#-#?#??-?####-?#???')
    family = factory.SubFactory(EquipmentFamilyFactory)
    calibration_date = factory.Faker('date')
    additional_properties = factory.Faker('pydict', value_types=['str', 'int', 'float', 'dict', 'list'])


class ScheduleFamilyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ScheduleFamily

    identifier = factory.SubFactory(ScheduleIdentifiersFactory)
    description = factory.Faker('sentence')
    ambient_temperature = factory.Faker('pyfloat', min_value=0.0, max_value=1000.0)
    pybamm_template = None
    additional_properties = factory.Faker('pydict', value_types=['str', 'int', 'float', 'dict', 'list'])


class ScheduleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Schedule

    family = factory.SubFactory(ScheduleFamilyFactory)
    schedule_file = None
    additional_properties = factory.Faker('pydict', value_types=['str', 'int', 'float', 'dict', 'list'])


class CyclerTestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CyclerTest

    cell_subject = factory.SubFactory(CellFactory)
    schedule = factory.SubFactory(ScheduleFactory)
    additional_properties = factory.Faker('pydict', value_types=['str', 'int', 'float', 'dict', 'list'])

    @factory.post_generation
    def equipment(self, create, extracted, **kwargs):
        if not create or not extracted:
            # Simple build, or nothing to add, do nothing.
            return

        # Add the iterable of equipment using bulk addition
        self.equipment.add(*extracted)


class ExperimentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Experiment

    title = factory.Faker('sentence')
    description = factory.Faker('sentence')
    additional_properties = factory.Faker('pydict', value_types=['str', 'int', 'float', 'dict', 'list'])

    @factory.post_generation
    def cycler_tests(self, create, extracted, **kwargs):
        if not create:
            # Simple build, or nothing to add, do nothing.
            return
        if not extracted:
            extracted = [CyclerTestFactory() for _ in range(3)]
        # Add the iterable of cycler tests using bulk addition
        self.cycler_tests.add(*extracted)

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if not create:
            # Simple build, or nothing to add, do nothing.
            return
        if not extracted:
            extracted = [UserFactory() for _ in range(3)]
        # Add the iterable of cycler tests using bulk addition
        self.authors.add(*extracted)


class ValidationSchemaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ValidationSchema

    name = factory.Faker('sentence')
    schema = factory.Faker('pydict', value_types=['str', 'int', 'float', 'dict', 'list'])