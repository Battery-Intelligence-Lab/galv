# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from .factories import UserFactory, \
    HarvesterFactory, \
    MonitoredPathFactory, \
    ObservedFileFactory
from galv.models import ObservedFile, \
    FileState

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class ObservedFileTests(APITestCase):
    def setUp(self):
        self.harvester = HarvesterFactory.create(name='Test Files')
        self.path = MonitoredPathFactory.create(harvester=self.harvester, path="/")
        self.files = ObservedFileFactory.create_batch(size=5)
        self.user = UserFactory.create(username='test_user')
        self.admin_user = UserFactory.create(username='test_user_admin')
        self.user.groups.add(self.harvester.user_group)
        self.admin_user.groups.add(self.path.admin_group)
        self.url = reverse('observedfile-detail', args=(self.files[0].id,))

    def test_view(self):
        self.client.force_login(self.user)
        print("Test rejection of view path")
        self.assertNotEqual(self.client.get(self.url).status_code, status.HTTP_200_OK)
        print("OK")
        self.client.force_login(self.admin_user)
        print("Test view path")
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_200_OK)
        print("OK")

    def test_reimport(self):
        self.client.force_login(self.admin_user)
        print("Test view path")
        url = reverse('observedfile-reimport', args=(self.files[0].id,))
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
        self.assertEqual(ObservedFile.objects.get(id=self.files[0].id).state, FileState.RETRY_IMPORT)
        print("OK")


if __name__ == '__main__':
    unittest.main()
