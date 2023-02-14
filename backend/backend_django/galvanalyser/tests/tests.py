import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from .factories import UserFactory
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

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class HarvesterTests(APITestCase):
    def test_create(self):
        url = reverse('harvester-list')
        user_id = 1
        harv = {
            'name': 'harv',
            'user': user_id
        }
        for request in [
            self.client.post(url, {}),  # name missing
            self.client.post(url, harv)  # no user with id
        ]:
            self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        UserFactory.create(id=user_id)
        self.assertEqual(self.client.post(url, harv).status_code, status.HTTP_200_OK)
        self.assertEqual(Harvester.objects.first().name, harv['name'])
        # name duplication error:
        self.assertEqual(self.client.post(url, harv).status_code, status.HTTP_400_BAD_REQUEST)

    def test_config(self):
        pass

    def test_update(self):
        pass

    def test_report(self):
        pass


class MonitoredPathTests(APITestCase):
    def setUp(self):
        pass

    def test_create(self):
        pass

    def test_update(self):
        pass


class ObservedFileTests(APITestCase):
    def setUp(self):
        pass

    def test_reimport(self):
        pass


class DatasetTests(APITestCase):
    def setUp(self):
        pass

    def test_update(self):
        pass


class CellFamilyTests(APITestCase):
    def setUp(self):
        pass

    def test_create(self):
        pass

    def test_update(self):
        pass


class CellTests(APITestCase):
    def setUp(self):
        pass

    def test_create(self):
        pass

    def test_update(self):
        pass


class EquipmentTests(APITestCase):
    def setUp(self):
        pass

    def test_create(self):
        pass

    def test_update(self):
        pass


if __name__ == '__main__':
    unittest.main()
