# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from .utils import assert_response_property
from .factories import ValidationSchemaFactory, CellFactory, ScheduleFactory, EquipmentFactory, ObservedFileFactory, \
    CyclerTestFactory, UserFactory
from galv.models import ValidationSchema

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class ValidationSchemaTests(APITestCase):
    def test_create(self):
        # Create ValidationSchema properties
        body = {
            'name': 'Test Schema',
            'schema': {'key': 'value', '$schema': 'http://json-schema.org/draft-07/schema#'},
        }
        url = reverse('validationschema-list')
        print("Test create ValidationSchema")
        response = self.client.post(url, body, format='json')
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_201_CREATED)
        print("OK")
        validation_schema = ValidationSchema.objects.get(id=response.json()['id'])
        self.assertEqual(validation_schema.name, body['name'])
        print("OK")

    def test_update(self):
        names = ['Test Schema 1', 'Test Schema 2']
        validation_schema = ValidationSchemaFactory.create(name=names[0])
        url = reverse('validationschema-detail', args=(validation_schema.id,))
        print("Test update ValidationSchema")
        response = self.client.patch(
            url,
            {'name': names[1]}
        )
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ValidationSchema.objects.get(id=validation_schema.id).name,
            names[1]
        )
        print("OK")


if __name__ == '__main__':
    unittest.main()
