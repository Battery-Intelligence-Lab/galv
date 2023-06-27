# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import os

import factory
import faker
import django.conf.global_settings
from django.utils import timezone
from galvanalyser.models import Harvester, \
    HarvestError, \
    MonitoredPath, \
    ObservedFile, \
    Cell, \
    CellFamily, \
    Dataset, \
    Equipment, \
    DataUnit, \
    DataColumnType, \
    DataColumn, \
    TimeseriesRangeLabel, \
    FileState
from django.contrib.auth.models import User, Group

fake = faker.Faker(django.conf.global_settings.LANGUAGE_CODE)


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
        user_group = GroupFactory.create(name=f"harvester_{obj.id}_user_group")
        admin_group = GroupFactory.create(name=f"harvester_{obj.id}_admin_group")
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
        user_group = GroupFactory.create(name=f"path_{obj.id}_user_group")
        admin_group = GroupFactory.create(name=f"path_{obj.id}_admin_group")
        obj.user_group = user_group
        obj.admin_group = admin_group
        obj.save()


class ObservedFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ObservedFile
        django_get_or_create = ('monitored_path', 'relative_path',)

    relative_path = factory.Faker('file_name')
    monitored_path = factory.SubFactory(MonitoredPathFactory)


class DatasetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dataset
        django_get_or_create = ('file', 'date',)

    file = factory.SubFactory(ObservedFileFactory)
    date = timezone.make_aware(timezone.datetime.now())


class CellFamilyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CellFamily

    name = factory.Faker('catch_phrase')
    form_factor = factory.Faker('bs')
    link_to_datasheet = factory.Faker('uri')
    anode_chemistry = factory.Faker('bs')
    cathode_chemistry = factory.Faker('bs')
    manufacturer = factory.Faker('company')
    nominal_capacity = factory.Faker('pyfloat', min_value=1.0, max_value=1000000.0)
    nominal_cell_weight = factory.Faker('pyfloat', min_value=1.0, max_value=1000000.0)


class CellFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cell

    uid = factory.Faker('bothify', text='?????-##??#-#?#??-?####-?#???')
    display_name = factory.Faker('catch_phrase')
    family = factory.SubFactory(CellFamilyFactory)


class EquipmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Equipment

    name = factory.Faker('catch_phrase')
    type = factory.Faker('bs')
