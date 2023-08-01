# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from .utils import assert_response_property
from .factories import CellFamilyFactory, CellFactory, CellModelsFactory
from galv.models import CellFamily, Cell, CellModels

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class CellFamilyTests(APITestCase):
    def test_create(self):
        body = {
            'model': 'Test CF', 'form_factor': 'test', 'datasheet': 'http://example.com',
            'chemistry': 'yes', 'nominal_capacity': 5.5, 'energy_density': 1.2, 'manufacturer': 'na'
        }
        url = reverse('cellfamily-list')
        print("Test create Cell Family")
        response = self.client.post(url, body)
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_201_CREATED)
        family_url = response.json().get('url')
        self.assertIsInstance(family_url, str)
        print("OK")
        print("Test create Cell")
        response = self.client.post(
            reverse('cell-list'),
            {'identifier': 'some-unique-id-1234', 'family': family_url}
        )
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_201_CREATED)
        print("OK")

    def test_update(self):
        cell_family = CellFamilyFactory.create(model=CellModelsFactory.create(value='Test family'))
        url = reverse('cellfamily-detail', args=(cell_family.uuid,))
        print("Test update Cell Family")
        response = self.client.patch(url, {'model': 'cell family'})
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        self.assertEqual(CellFamily.objects.get(uuid=cell_family.uuid).model.value, 'cell family')
        # Also check that the CellModels object was updated
        self.assertTrue(CellModels.objects.filter(value='cell family').exists())
        print("OK")
        print("Test update Cell")
        cell = CellFactory.create(family=cell_family)
        url = reverse('cell-detail', args=(cell.uuid,))
        response = self.client.patch(url, {'identifier': 'c123'})
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        self.assertEqual(Cell.objects.get(uuid=cell.uuid).identifier, 'c123')
        response = self.client.patch(url, {'identifier': 'ddd-x12'})
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        self.assertEqual(Cell.objects.get(uuid=cell.uuid).identifier, 'ddd-x12')
        print("OK")


if __name__ == '__main__':
    unittest.main()
