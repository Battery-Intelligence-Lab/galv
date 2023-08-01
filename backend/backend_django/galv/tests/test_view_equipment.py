# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from backend.backend_django.galv.tests.utils import assert_response_property
from .factories import EquipmentFactory
from galv.models import Equipment

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class EquipmentTests(APITestCase):
    def test_create(self):
        # Create EquipmentFamily
        body = {'type': 'test_type', 'manufacturer': 'test_manufacturer', 'model': 'test_model'}
        url = reverse('equipmentfamily-list')
        print("Test create EquipmentFamily")
        response = self.client.post(url, body)
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_201_CREATED)
        print("OK")

        print("Test create Equipment")
        body = {'identifier': 'Test EQ', 'family': response.json()['url'], 'serial_number': 'test_serial_number'}
        url = reverse('equipment-list')
        response = self.client.post(url, body)
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_201_CREATED)
        equipment = Equipment.objects.get(uuid=response.json()['uuid'])
        self.assertEqual(equipment.identifier, 'Test EQ')
        self.assertEqual(equipment.family.type.value, 'test_type')
        self.assertEqual(equipment.additional_properties['serial_number'], 'test_serial_number')
        print("OK")

    def test_update(self):
        equipment = EquipmentFactory.create(identifier='Test kit')
        url = reverse('equipment-detail', args=(equipment.uuid,))
        print("Test update Equipment")
        response = self.client.patch(url, {'identifier': 'New kit'})
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        self.assertEqual(Equipment.objects.get(uuid=equipment.uuid).identifier, 'New kit')
        print("OK")


if __name__ == '__main__':
    unittest.main()
