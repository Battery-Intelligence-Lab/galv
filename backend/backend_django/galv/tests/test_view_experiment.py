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
from .factories import ExperimentFactory, CellFactory, ScheduleFactory, EquipmentFactory, ObservedFileFactory, \
    CyclerTestFactory, UserFactory
from galv.models import Experiment

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class ExperimentTests(APITestCase):
    def test_create(self):
        # Create Experiment properties
        cycler_tests = CyclerTestFactory.create_batch(size=4)
        authors = UserFactory.create_batch(size=4)

        body = {
            'title': 'Test Experiment',
            'description': 'Test Experiment Description',
            'authors': [reverse('user-detail', args=(u.id,)) for u in authors],
            'cycler_tests': [reverse('cyclertest-detail', args=(ct.uuid,)) for ct in cycler_tests]
        }
        url = reverse('experiment-list')
        print("Test create Experiment")
        response = self.client.post(url, body, format='json')
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_201_CREATED)
        print("OK")
        experiment = Experiment.objects.get(uuid=response.json()['uuid'])
        self.assertEqual(experiment.title, body['title'])
        [self.assertEqual(str(ct.uuid), str(cycler_tests[i].uuid)) for i, ct in enumerate(experiment.cycler_tests.all())]
        [self.assertEqual(str(a.id), str(authors[i].id)) for i, a in enumerate(experiment.authors.all())]
        print("OK")

    def test_update(self):
        cycler_tests = CyclerTestFactory.create_batch(size=2)
        experiment = ExperimentFactory.create(cycler_tests=[cycler_tests[0]])
        url = reverse('experiment-detail', args=(experiment.uuid,))
        print("Test update Experiment")
        response = self.client.patch(
            url,
            {'cycler_tests': [reverse('cyclertest-detail', args=(cycler_tests[1].uuid,))]}
        )
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(Experiment.objects.get(uuid=experiment.uuid).cycler_tests.all()[0].uuid),
            str(cycler_tests[1].uuid)
        )
        print("OK")


if __name__ == '__main__':
    unittest.main()
