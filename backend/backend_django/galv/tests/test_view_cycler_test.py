# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from backend.backend_django.galv.tests.utils import assert_response_property
from .factories import CyclerTestFactory, CellFactory, ScheduleFactory, EquipmentFactory, ObservedFileFactory
from galv.models import CyclerTest

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class CyclerTestTests(APITestCase):
    def test_create(self):
        # Create CyclerTest properties
        cell_subject = CellFactory.create()
        schedule = ScheduleFactory.create()
        equipment = EquipmentFactory.create_batch(size=4)
        file = ObservedFileFactory.create()

        body = {
            'cell_subject': reverse('cell-detail', args=(cell_subject.uuid,)),
            'schedule': reverse('schedule-detail', args=(schedule.uuid,)),
            'equipment': [reverse('equipment-detail', args=(e.uuid,)) for e in equipment],
            'observed_file': reverse('observedfile-detail', args=(file.uuid,)),
            'some other property': 'some other value'
        }
        url = reverse('cyclertest-list')
        print("Test create CyclerTest")
        response = self.client.post(url, body, format='json')
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_201_CREATED)
        print("OK")
        cycler_test = CyclerTest.objects.get(uuid=response.json()['uuid'])
        self.assertEqual(str(cycler_test.cell_subject.uuid), str(cell_subject.uuid))
        [self.assertEqual(str(e.uuid), str(equipment[i].uuid)) for i, e in enumerate(cycler_test.equipment.all())]
        self.assertEqual(cycler_test.additional_properties['some other property'], 'some other value')
        print("OK")

    def test_update(self):
        cell_subjects = CellFactory.create_batch(size=2)
        cycler_test = CyclerTestFactory.create(cell_subject=cell_subjects[0])
        url = reverse('cyclertest-detail', args=(cycler_test.uuid,))
        print("Test update CyclerTest")
        response = self.client.patch(
            url,
            {'cell_subject': reverse('cell-detail', args=(cell_subjects[1].uuid,))}
        )
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(CyclerTest.objects.get(uuid=cycler_test.uuid).cell_subject.uuid),
            str(cell_subjects[1].uuid)
        )
        print("OK")


if __name__ == '__main__':
    unittest.main()
