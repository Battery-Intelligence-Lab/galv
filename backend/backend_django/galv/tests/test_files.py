# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import unittest
from django.urls import reverse
from rest_framework import status
import logging

from .utils import assert_response_property, GalvTestCase
from .factories import HarvesterFactory, \
    MonitoredPathFactory, \
    ObservedFileFactory, fake
from galv.models import ObservedFile, FileState

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class ObservedFileTests(GalvTestCase):
    stub = 'observedfile'
    factory = ObservedFileFactory

    def setUp(self):
        super().setUp()
        self.harvester = HarvesterFactory.create(name='Test Files', lab=self.lab)
        self.specific_path = MonitoredPathFactory.create(harvester=self.harvester, path="/specific", team=self.lab_team)
        self.other_path = MonitoredPathFactory.create(harvester=self.harvester, path="/other", team=self.lab_other_team)
        self.regex_path = MonitoredPathFactory.create(harvester=self.harvester, path="/", regex="abc/.*", team=self.lab_team)
        self.specific_files = ObservedFileFactory.create_batch(size=2, harvester=self.harvester, path_root=self.specific_path.path)
        self.other_files = ObservedFileFactory.create_batch(size=3, harvester=self.harvester, path_root=self.other_path.path)
        self.regex_files = ObservedFileFactory.create_batch(size=6, harvester=self.harvester, path_root=f"{self.regex_path.path}/abc")
        self.other_harvester = HarvesterFactory.create(name='Test Files Other', lab=self.strange_lab)
        self.other_harvester_path = MonitoredPathFactory.create(harvester=self.other_harvester, path="/", team=self.strange_lab_team)
        self.other_harvester_files = ObservedFileFactory.create_batch(size=4, harvester=self.other_harvester, path_root=self.other_harvester_path.path)

    def get_edit_kwargs(self):
        return {'name': fake.file_name()}

    def test_create_rejected(self):
        for user, login in {
            'user': lambda: self.client.force_authenticate(self.user),
            'admin': lambda: self.client.force_authenticate(self.admin),
            'other': lambda: self.client.force_authenticate(self.lab_admin),
            'stranger': lambda: self.client.force_authenticate(self.strange_lab_admin),
            'anonymous': lambda: self.client.logout(),
        }.items():
            with self.subTest(user=user):
                login()
                response = self.client.post(reverse(f'{self.stub}-list'), data=self.get_edit_kwargs())
                assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list(self):
        for user, details in {
            'user': {'login': lambda: self.client.force_authenticate(self.user), 'expected_set': [*self.specific_files, *self.regex_files]},
            'admin': {'login': lambda: self.client.force_authenticate(self.admin), 'expected_set': [*self.specific_files, *self.regex_files]},
            'lab_admin': {'login': lambda: self.client.force_authenticate(self.lab_admin), 'expected_set': []},
            'stranger': {'login': lambda: self.client.force_authenticate(self.strange_lab_admin), 'expected_set': [*self.other_harvester_files]},
            'anonymous': {'login': lambda: self.client.logout(), 'expected_set': []},
        }.items():
            with self.subTest(user=user):
                details['login']()
                response = self.client.get(reverse(f'{self.stub}-list'))
                assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
                self.assertEqual(len(response.json()), len(details['expected_set']))
                for file in details['expected_set']:
                    self.assertIn(str(file.uuid), [p['uuid'] for p in response.json()])

    def test_read(self):
        for user, details in {
            'user': {'login': lambda: self.client.force_authenticate(self.user), 'code': 200},
            'admin': {'login': lambda: self.client.force_authenticate(self.admin), 'code': 200},
            'other': {'login': lambda: self.client.force_authenticate(self.lab_admin), 'code': 403},
            'stranger': {'login': lambda: self.client.force_authenticate(self.strange_lab_admin), 'code': 403},
            'anonymous': {'login': lambda: self.client.logout(), 'code': 401},
        }.items():
            with self.subTest(user=user):
                details['login']()
                response = self.client.get(reverse(f'{self.stub}-detail', args=(self.specific_files[0].uuid,)))
                assert_response_property(self, response, self.assertEqual, response.status_code, details['code'])
                if response.status_code == 200:
                    self.assertEqual(response.json()['uuid'], str(self.specific_files[0].uuid))

    def test_update(self):
        for user, details in {
            'user': {'login': lambda: self.client.force_authenticate(self.user), 'code': 200},
            'admin': {'login': lambda: self.client.force_authenticate(self.admin), 'code': 200},
            'other': {'login': lambda: self.client.force_authenticate(self.lab_admin), 'code': 403},
            'stranger': {'login': lambda: self.client.force_authenticate(self.strange_lab_admin), 'code': 403},
            'anonymous': {'login': lambda: self.client.logout(), 'code': 401},
        }.items():
            with self.subTest(user=user):
                details['login']()
                response = self.client.patch(reverse(f'{self.stub}-detail', args=(self.specific_files[0].uuid,)), data=self.get_edit_kwargs(), format='json')
                assert_response_property(self, response, self.assertEqual, response.status_code, details['code'])

    def test_destroy_rejected(self):
        for user, login in {
            'user': lambda: self.client.force_authenticate(self.user),
            'admin': lambda: self.client.force_authenticate(self.admin),
            'other': lambda: self.client.force_authenticate(self.lab_admin),
            'stranger': lambda: self.client.force_authenticate(self.strange_lab_admin),
            'anonymous': lambda: self.client.logout(),
        }.items():
            with self.subTest(user=user):
                login()
                response = self.client.delete(reverse(f'{self.stub}-list'), data=self.get_edit_kwargs())
                assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_reimport(self):
        for user, details in {
            'user': {'login': lambda: self.client.force_authenticate(self.user), 'code': 200},
            'admin': {'login': lambda: self.client.force_authenticate(self.admin), 'code': 200},
            'other': {'login': lambda: self.client.force_authenticate(self.lab_admin), 'code': 403},
            'stranger': {'login': lambda: self.client.force_authenticate(self.strange_lab_admin), 'code': 403},
            'anonymous': {'login': lambda: self.client.logout(), 'code': 401},
        }.items():
            with self.subTest(user=user):
                self.specific_files[0].state = FileState.IMPORTED
                self.specific_files[0].save()
                details['login']()
                response = self.client.get(reverse(f'{self.stub}-reimport', args=(self.specific_files[0].uuid,)))
                assert_response_property(self, response, self.assertEqual, response.status_code, details['code'])
                if response.status_code == 200:
                    self.assertEqual(response.json()['state'], FileState.RETRY_IMPORT)


if __name__ == '__main__':
    unittest.main()
