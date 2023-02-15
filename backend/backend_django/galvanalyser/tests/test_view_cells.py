import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from .factories import CellFamilyFactory, CellFactory
from galvanalyser.models import CellFamily, Cell

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class CellFamilyTests(APITestCase):
    def test_create(self):
        body = {
            'name': 'Test CF', 'form_factor': 'test', 'link_to_datasheet': 'http',
            'anode_chemistry': 'yes','cathode_chemistry': 'yes',
            'nominal_capacity': 5.5, 'nominal_cell_weight': 1.2, 'manufacturer': 'na'
        }
        url = reverse('cellfamily-list')
        print("Test create Cell Family")
        response = self.client.post(url, body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        family_url = response.json().get('url')
        self.assertIsInstance(family_url, str)
        print("OK")
        print("Test create Cell")
        response = self.client.post(reverse('cell-list'), {'display_name': 'test cell', 'family': family_url})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("OK")

    def test_update(self):
        cell_family = CellFamilyFactory.create(name='Test family')
        url = reverse('cellfamily-detail', args=(cell_family.id,))
        print("Test update Cell Family")
        response = self.client.patch(url, {'name': 'cell family'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CellFamily.objects.get(id=cell_family.id).name, 'cell family')
        print("OK")
        print("Test update Cell")
        cell = CellFactory.create(family=cell_family)
        url = reverse('cell-detail', args=(cell.id,))
        response = self.client.patch(url, {'display_name': 'c123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Cell.objects.get(id=cell.id).display_name, 'c123')
        print("OK")


if __name__ == '__main__':
    unittest.main()
