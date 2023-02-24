import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from .factories import EquipmentFactory
from galvanalyser.models import Equipment

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class EquipmentTests(APITestCase):
    def test_create(self):
        body = {'name': 'Test EQ', 'type': 'test'}
        url = reverse('equipment-list')
        print("Test create Equipment")
        response = self.client.post(url, body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("OK")

    def test_update(self):
        equipment = EquipmentFactory.create(name='Test kit')
        url = reverse('equipment-detail', args=(equipment.id,))
        print("Test update Equipment")
        response = self.client.patch(url, {'name': 'New kit'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Equipment.objects.get(id=equipment.id).name, 'New kit')
        print("OK")


if __name__ == '__main__':
    unittest.main()
