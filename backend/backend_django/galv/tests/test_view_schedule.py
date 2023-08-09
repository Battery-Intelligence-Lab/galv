# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import os
import unittest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from backend.backend_django.galv.tests.utils import assert_response_property
from .factories import ScheduleFactory
from galv.models import Schedule

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class ScheduleTests(APITestCase):
    def test_create(self):
        # Create ScheduleFamily
        body = {'identifier': 'Charge to Maximum', 'description': 'this is a public service annoucement', 'ambient_temperature': 21.0}
        url = reverse('schedulefamily-list')
        print("Test create ScheduleFamily")
        response = self.client.post(url, body)
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_201_CREATED)
        print("OK")

        print("Test create Schedule missing schedule_file")
        body = {'family': response.json()['url'], 'type': 'only a test'}
        url = reverse('schedule-list')
        response = self.client.post(url, body)
        assert_response_property(
            self,
            response,
            self.assertEqual,
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")
        print("Test create Schedule ok")
        f_name = "__schedule_file.tmp"
        body = {
            **body,
            "schedule_file": SimpleUploadedFile(
                f_name,
                b"file_content",
                content_type="text/plain"
            )
        }
        try:
            response = self.client.post(url, body)
            assert_response_property(
                self,
                response,
                self.assertEqual,
                response.status_code,
                status.HTTP_201_CREATED
            )
            schedule = Schedule.objects.get(uuid=response.json()['uuid'])
            self.assertEqual(schedule.family.identifier.value, 'Charge to Maximum')
            self.assertEqual(schedule.additional_properties['type'], 'only a test')
        finally:
            os.unlink(f_name)
        print("OK")

    def test_update(self):
        schedule = ScheduleFactory.create(
            pybamm_schedule_variables={'test_ok': False},
            family__pybamm_template=["test ok: {test_ok}"]
        )
        url = reverse('schedule-detail', args=(schedule.uuid,))
        print("Test update Schedule")
        response = self.client.patch(url, {'pybamm_schedule_variables': {'test_ok': True}}, format='json')
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        self.assertEqual(Schedule.objects.get(uuid=schedule.uuid).pybamm_schedule_variables.get('test_ok'), True)
        print("OK")


if __name__ == '__main__':
    unittest.main()
