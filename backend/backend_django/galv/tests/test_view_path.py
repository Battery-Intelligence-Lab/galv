# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import json
import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from .factories import UserFactory, \
    HarvesterFactory, \
    MonitoredPathFactory
from galv.models import Harvester, \
    MonitoredPath

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class MonitoredPathTests(APITestCase):
    def setUp(self):
        self.path = '/path/to/data'
        self.harvester = HarvesterFactory.create(name='Test Paths')
        self.non_user = UserFactory.create(username='test_paths')
        self.user = UserFactory.create(username='test_paths_user')
        self.user.groups.add(self.harvester.user_group)
        self.admin_user = UserFactory.create(username='test_paths_admin')
        self.admin_user.groups.add(self.harvester.admin_group)

    def test_create(self):
        self.client.force_login(self.non_user)
        url = reverse('monitoredpath-list')
        print("Test rejection of Create Path - no authorisation")
        body = {
            'path': self.path,
            'regex': '.*',
            'harvester': reverse('harvester-detail', args=(self.harvester.uuid,)),
            'stable_time': 60
        }
        self.assertEqual(
            self.client.post(url, body).status_code,
            status.HTTP_403_FORBIDDEN
        )
        print("OK")
        self.client.force_login(self.user)
        print("Test rejection of Create Path - no path")
        no_path = {**body}
        no_path.pop('path')
        self.assertEqual(
            self.client.post(url, no_path).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")
        print("Test rejection of Create Path - invalid harvester")
        i = 1 if self.harvester.uuid != 1 else 2
        self.assertEqual(
            self.client.post(url, {'harvester': i}).status_code,
            status.HTTP_403_FORBIDDEN
        )
        print("OK")
        print("Test successful Path creation")
        self.client.force_login(self.admin_user)
        self.assertEqual(
            self.client.post(url, body).status_code,
            status.HTTP_201_CREATED
        )
        print("OK")
        print("Test rejection of duplicate name")
        self.assertEqual(
            self.client.post(url, body).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")

    def test_update(self):
        path = MonitoredPathFactory.create(path=self.path, harvester=self.harvester)
        self.admin_user.groups.add(path.admin_group)
        url = reverse('monitoredpath-detail', args=(path.uuid,))
        print("Test update rejected - authorisation")
        self.client.force_login(self.user)
        body = {'path': path.path, 'regex': '^abc', 'stable_time': 100}
        self.assertEqual(
            self.client.patch(url, body).status_code,
            status.HTTP_404_NOT_FOUND
        )
        print("OK")
        print("Test update okay")
        self.client.force_login(self.admin_user)
        body = {'path': path.path, 'regex': '^abc', 'stable_time': 1}
        self.assertEqual(
            self.client.patch(url, body).status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            MonitoredPath.objects.get(path=path.path, harvester=self.harvester).stable_time,
            body.get('stable_time')
        )
        self.assertEqual(
            MonitoredPath.objects.get(path=path.path, harvester=self.harvester).regex,
            body.get('regex')
        )
        print("OK")


if __name__ == '__main__':
    unittest.main()
