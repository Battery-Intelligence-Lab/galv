# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from .utils import assert_response_property
from .factories import UserFactory, \
    HarvesterFactory, \
    DatasetFactory, MonitoredPathFactory

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class DatasetTests(APITestCase):
    def setUp(self):
        self.harvester = HarvesterFactory.create(name='Test Dataset')
        self.dataset = DatasetFactory.create(file__harvester=self.harvester)
        self.monitored_path = MonitoredPathFactory.create(harvester=self.harvester, path="/")
        self.user = UserFactory.create(username='test_user')
        self.admin_user = UserFactory.create(username='test_user_admin')
        self.user.groups.add(self.harvester.user_group)
        self.admin_user.groups.add(self.monitored_path.admin_group)
        self.url = reverse('dataset-detail', args=(self.dataset.uuid,))

    def test_view(self):
        self.client.force_login(self.user)
        print("Test rejection of dataset view")
        response = self.client.get(self.url)
        assert_response_property(self, response, self.assertNotEqual, response.status_code, status.HTTP_200_OK)
        print("OK")
        self.client.force_login(self.admin_user)
        print("Test dataset view")
        response = self.client.get(self.url)
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        print("OK")


if __name__ == '__main__':
    unittest.main()
