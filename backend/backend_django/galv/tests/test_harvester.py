# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.
import json
import unittest
from django.urls import reverse
from rest_framework import status
import logging

from .utils import assert_response_property, GalvTestCase
from .factories import UserFactory, \
    HarvesterFactory, \
    MonitoredPathFactory
from galv.models import Harvester, \
    HarvesterEnvVar, \
    HarvestError, \
    MonitoredPath, \
    ObservedFile, \
    FileState, \
    DataColumn, \
    TimeseriesDataInt

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class HarvesterTests(GalvTestCase):
    stub = 'harvester'
    factory = HarvesterFactory

    def get_edit_kwargs(self):
        try:
            s = self.client.handler._force_user.username
        except AttributeError:
            try:
                s = self.client._credentials['HTTP_AUTHORIZATION'][:len('Harvester 0000')]
                s = f"{s}..."
            except KeyError:
                s = 'anonymous'
        return {'name': f'Harvester_edited_by_{s}'}

    def setUp(self):
        super().setUp()
        self.harvester = HarvesterFactory.create(name='Test Harvester', lab=self.lab)
        self.other_harvester = HarvesterFactory.create(name='Other Harvester', lab=self.lab)

    def test_create_unauthorised(self):
        for user, login in {
            'user': lambda: self.client.force_authenticate(self.user),
            'admin': lambda: self.client.force_authenticate(self.admin),
            'anonymous': lambda: self.client.logout()
        }.items():
            with self.subTest(user=user):
                login()
                url = reverse(f'{self.stub}-list')
                create_dict = self.dict_factory(lab={'id': self.lab.id}, name=f'create_unauth_Harvester {user}')
                response = self.client.post(url, create_dict, format='json')
                assert_response_property(
                    self, response, self.assertGreaterEqual, response.status_code,
                    400, msg=f"Check {user} can't create Harvester"
                )

    def test_cannot_create_in_other_lab(self):
        self.client.force_authenticate(self.lab_admin)
        url = reverse(f'{self.stub}-list')
        create_dict = self.dict_factory(lab={'id': self.strange_lab.id}, name=f'create_badlab_Harvester')
        response = self.client.post(url, create_dict, format='json')
        assert_response_property(
            self, response, self.assertEqual, response.status_code,
            400, msg=f"Check {self.lab_admin.username} cannot create Harvester on {self.strange_lab}"
        )

    def test_create_lab_admin(self):
        self.client.force_authenticate(self.lab_admin)
        url = reverse(f'{self.stub}-list')
        create_dict = self.dict_factory(lab={'id': self.lab.id}, name=f'create_Harvester')
        response = self.client.post(url, create_dict, format='json')
        assert_response_property(
            self, response, self.assertEqual, response.status_code,
            201, msg=f"Check {self.lab_admin.username} can create Harvester on {self.lab}"
        )

    def test_read_config_rejection(self):
        for user, login in {
            'user': lambda: self.client.force_authenticate(self.user),
            'admin': lambda: self.client.force_authenticate(self.admin),
            'lab_admin': lambda: self.client.force_authenticate(self.lab_admin),
            'anonymous': lambda: self.client.logout()
        }.items():
            with self.subTest(user=user):
                login()
                url = reverse(f'{self.stub}-config', args=(self.harvester.uuid,))
                response = self.client.get(url)
                assert_response_property(
                    self, response, self.assertGreaterEqual, response.status_code,
                    400, msg=f"Check users can't access harvester config"
                )

    def test_harvester_read_config_rejection(self):
        for token in [
            'bad_token',
            self.other_harvester.api_key
        ]:
            self.client._credentials = {'HTTP_AUTHORIZATION': f'Harvester {token}'}
            url = reverse(f'{self.stub}-config', args=(self.harvester.uuid,))
            response = self.client.get(url)
            assert_response_property(
                self, response, self.assertEqual, response.status_code,
                401, msg=f"Check can't access harvester config with token {token}"
            )

    def test_harvester_read_config(self):
        self.client._credentials = {'HTTP_AUTHORIZATION': f'Harvester {self.harvester.api_key}'}
        url = reverse(f'{self.stub}-config', args=(self.harvester.uuid,))
        response = self.client.get(url)
        assert_response_property(
            self, response, self.assertEqual, response.status_code,
            200, msg=f"Check harvester can access own config"
        )

    def test_list(self):
        for user, details in {
            'user': {'harvesters': [self.harvester, self.other_harvester], 'login': lambda: self.client.force_authenticate(self.user)},
            'admin': {'harvesters': [self.harvester, self.other_harvester], 'login': lambda: self.client.force_authenticate(self.admin)},
            'lab_admin': {'harvesters': [self.harvester, self.other_harvester], 'login': lambda: self.client.force_authenticate(self.lab_admin)},
            'strange_lab_admin': {'harvesters': [], 'login': lambda: self.client.force_authenticate(self.strange_lab_admin)},
            'anonymous': {'harvesters': [], 'login': lambda: self.client.logout()}
        }.items():
            with self.subTest(user=user):
                details['login']()
                url = reverse(f'{self.stub}-list')
                response = self.client.get(url)
                assert_response_property(
                    self, response, self.assertEqual, response.status_code,
                    200, msg=f"Check {user} can list harvesters"
                )
                json = response.json()
                self.assertEqual(len(json), len(details['harvesters']))
                for h in details['harvesters']:
                    self.assertIn(str(h.uuid), [h['uuid'] for h in json])

    def test_read_rejected(self):
        for user, login in {
            'strange_lab_admin':  lambda: self.client.force_authenticate(self.strange_lab_admin),
            'anonymous': lambda: self.client.logout(),
            'other_harvester': lambda: self.client._credentials.update({'HTTP_AUTHORIZATION': f'Harvester {self.other_harvester.api_key}'})
        }.items():
            with self.subTest(user=user):
                login()
                url = reverse(f'{self.stub}-detail', args=(self.harvester.uuid,))
                response = self.client.get(url)
                assert_response_property(
                    self, response, self.assertGreaterEqual, response.status_code,
                    400, msg=f"Check {user} cannot read {self.harvester}"
                )

    def test_read(self):
        for user, login in {
            'user': lambda: self.client.force_authenticate(self.user),
            'admin': lambda: self.client.force_authenticate(self.admin),
            'lab_admin': lambda: self.client.force_authenticate(self.lab_admin),
            'harvester': lambda: self.client._credentials.update({'HTTP_AUTHORIZATION': f'Harvester {self.harvester.api_key}'}),
        }.items():
            with self.subTest(user=user):
                login()
                url = reverse(f'{self.stub}-detail', args=(self.harvester.uuid,))
                response = self.client.get(url)
                assert_response_property(
                    self, response, self.assertEqual, response.status_code,
                    200, msg=f"Check {user} can read {self.harvester}"
                )
                self.assertEqual('environment_variables' in response.json(), user in ['harvester', 'lab_admin'])

    def test_update_rejected(self):
        for user, login in {
            'user': lambda: self.client.force_authenticate(self.user),
            'admin': lambda: self.client.force_authenticate(self.admin),
            'strange_lab_admin': lambda: self.client.force_authenticate(self.strange_lab_admin),
            'anonymous': lambda: self.client.logout(),
            'other_harvester': lambda: self.client._credentials.update({'HTTP_AUTHORIZATION': f'Harvester {self.other_harvester.api_key}'})
        }.items():
            with self.subTest(user=user):
                login()
                url = reverse(f'{self.stub}-detail', args=(self.harvester.uuid,))
                response = self.client.patch(url, self.get_edit_kwargs(), format='json')
                assert_response_property(
                    self, response, self.assertGreaterEqual, response.status_code,
                    400, msg=f"Check {user} cannot update {self.harvester}"
                )

    def test_update(self):
        for user, login in {
            'lab_admin': lambda: self.client.force_authenticate(self.lab_admin),
            'harvester': lambda: self.client._credentials.update({'HTTP_AUTHORIZATION': f'Harvester {self.harvester.api_key}'}),
        }.items():
            with self.subTest(user=user):
                login()
                url = reverse(f'{self.stub}-detail', args=(self.harvester.uuid,))
                response = self.client.patch(url, self.get_edit_kwargs(), format='json')
                assert_response_property(
                    self, response, self.assertEqual, response.status_code,
                    200, msg=f"Check {user} can update {self.harvester}"
                )
                self.assertEqual(response.json()['name'], self.get_edit_kwargs()['name'])

    def test_destroy_rejected(self):
        self.client.force_authenticate(self.lab_admin)
        url = reverse(f'{self.stub}-detail', args=(self.harvester.uuid,))
        response = self.client.delete(url)
        assert_response_property(
            self, response, self.assertEqual, response.status_code,
            405, msg=f"Check delete harvester is not allowed"
        )

    def test_report_unauthorized(self):
        self.client.force_authenticate(self.lab_admin)
        url = reverse(f'{self.stub}-report', args=(self.harvester.uuid,))
        response = self.client.post(url, {'status': 'success'})
        assert_response_property(
            self, response, self.assertEqual, response.status_code,
            403, msg=f"Check manual harvester report is not allowed"
        )

    def test_report(self):
        mp = MonitoredPathFactory.create(harvester=self.harvester)
        f = ObservedFile.objects.create(path='/a/b/c/d.ext', harvester=self.harvester)
        self.client._credentials = {'HTTP_AUTHORIZATION': f'Harvester {self.harvester.api_key}'}
        url = reverse(f'{self.stub}-report', args=(self.harvester.uuid,))

        def check_response(response, *args, **kwargs):
            assertion = kwargs.pop('assertion', self.assertEqual)
            msg = kwargs.pop('msg', f"Check harvester report received: [{response.status_code}] {response.json()}")
            assertion(*args, **kwargs, msg=msg)


        for report in [
            {
                'name': 'no_status',
                'data': {},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_400_BAD_REQUEST),
                ]
            },
            {
                'name': 'error_none',
                'data': {'status': 'error', 'path': '/a/b/c.ext'},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_400_BAD_REQUEST)
                ]
            },
            {
                'name': 'error_str',
                'data': {'status': 'error', 'path': '/a/b/c.ext', 'error': 'test'},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_200_OK),
                    lambda r: check_response(r, HarvestError.objects.filter(error='test').count(), 1),
                ]
            },
            {
                'name': 'error_str',
                'data': {'status': 'error', 'path': '/a/b/c.ext', 'error': {'test': 'test'}},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_200_OK),
                    lambda r: check_response(r, HarvestError.objects.filter(error=json.dumps({'test': 'test'})).count(), 1),
                ]
            },
            {
                'name': 'no_path',
                'data': {'status': 'success'},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_400_BAD_REQUEST),
                ]
            },
            {
                'name': 'no_monitored_path',
                'data': {'status': 'success', 'path': '/a/b/c.ext'},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_400_BAD_REQUEST),
                ]
            },
            {
                'name': 'file_size_no_size',
                'data': {'status': 'success', 'path': '/a/b/c.ext', 'monitored_path_uuid': mp.uuid, 'content': {'task': 'file_size'}},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_400_BAD_REQUEST),
                ]
            },
            {
                'name': 'file_size',
                'data': {'status': 'success', 'path': '/a/b/c.ext', 'monitored_path_uuid': mp.uuid, 'content': {'task': 'file_size', 'size': 1024}},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_200_OK),
                    lambda r: check_response(r, ObservedFile.objects.filter(path='/a/b/c.ext').count(), 1),
                    lambda r: check_response(r, r.json()['uuid'], str(ObservedFile.objects.get(path='/a/b/c.ext').uuid))
                ]
            },
            {
                'name': 'import_unrecognised',
                'data': {'status': 'success', 'path': '/a/b/c.ext', 'monitored_path_uuid': mp.uuid, 'content': {'task': 'import'}},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_400_BAD_REQUEST),
                ]
            },
            {
                'name': 'import_nonexistent_file',
                'data': {'status': 'success', 'path': 'foo/bar.ext', 'monitored_path_uuid': mp.uuid, 'content': {'task': 'import'}},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_400_BAD_REQUEST),
                ]
            },
            {
                'name': 'import_unknown_status',
                'data': {'status': 'success', 'path': f.path, 'monitored_path_uuid': mp.uuid, 'content': {'task': 'import', 'status': 'unknown'}},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_400_BAD_REQUEST),
                ]
            },
            {
                'name': 'import_begin',
                'data': {'status': 'success', 'path': f.path, 'monitored_path_uuid': mp.uuid, 'content': {
                    'task': 'import',
                    'status': 'begin',
                    'test_date': 0.0,
                    'core_metadata': {},
                    'extra_metadata': {}
                }},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_200_OK),
                    lambda r: check_response(r, r.json()['uuid'], str(ObservedFile.objects.get(path=f.path).uuid)),
                    lambda r: check_response(r, ObservedFile.objects.get(uuid=f.uuid).state, FileState.IMPORTING)
                ]
            },
            {
                'name': 'import_complete',
                'data': {'status': 'success', 'path': f.path, 'monitored_path_uuid': mp.uuid, 'content': {
                    'task': 'import',
                    'status': 'complete'
                }},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_200_OK),
                    lambda r: check_response(r, r.json()['uuid'], str(ObservedFile.objects.get(path=f.path).uuid)),
                    lambda r: check_response(r, ObservedFile.objects.get(uuid=f.uuid).state, FileState.IMPORTED)
                ],
            },
            {
                'name': 'import_failed',
                'data': {'status': 'success', 'path': f.path, 'monitored_path_uuid': mp.uuid, 'content': {
                    'task': 'import',
                    'status': 'failed'
                }},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_200_OK),
                    lambda r: check_response(r, r.json()['uuid'], str(ObservedFile.objects.get(path=f.path).uuid)),
                    lambda r: check_response(r, ObservedFile.objects.get(uuid=f.uuid).state, FileState.IMPORT_FAILED)
                ],
            },
            {
                'name': 'import_in_progress',
                'data': {'status': 'success', 'path': f.path, 'monitored_path_uuid': mp.uuid, 'content': {
                    'task': 'import',
                    'status': 'in_progress',
                    'data': [
                        {'unit_symbol': "s", 'data_type': 'int', 'column_name': "sometimes", 'values': [7, 8, 9]}
                    ]
                }},
                'checks': [
                    lambda r: check_response(r, r.status_code, status.HTTP_200_OK),
                    lambda r: check_response(r, r.json()['uuid'], str(ObservedFile.objects.get(path=f.path).uuid)),
                ]
            }
        ]:
            with self.subTest(report=report['name']):
                response = self.client.post(url, report['data'], format='json')
                for check in report['checks']:
                    check(response)


if __name__ == '__main__':
    unittest.main()
