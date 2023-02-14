import factory
import faker
import django.conf.global_settings
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
    DataColumnStringKeys, \
    DataColumn, \
    TimeseriesData, \
    TimeseriesRangeLabel, \
    FileState
from django.contrib.auth.models import User, Group

fake = faker.Faker(django.conf.global_settings.LANGUAGE_CODE)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('id',)

    id = factory.Faker('random_int', min=1, max=10000)
