# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
from django.urls import reverse
from rest_framework import status
import logging

from .utils import GalvTestCase, assert_response_property
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
    def test_create(self):
        url = reverse('harvester-list')
        user_id = 1
        user = UserFactory.create(id=user_id)
        harv = {
            'name': 'harv',
            'user': reverse('user-detail', args=(user_id,))
        }
        user.is_active = False
        user.save()
        print("Test rejection of Create Harvester with no name, user_id")
        for request in [
            self.client.post(url, {}),  # name missing
            self.client.post(url, harv)  # no user with id
        ]:
            self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        print("OK")
        user.is_active = True
        user.save()
        print("Test successful Harvester creation")
        request = self.client.post(url, harv)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Harvester.objects.first().name, harv['name'])
        self.assertIn('api_key', request.json())
        print("OK")
        print("Test rejection of duplicate name")
        # name duplication error:
        self.assertEqual(self.client.post(url, harv).status_code, status.HTTP_400_BAD_REQUEST)
        print("OK")

    def test_config(self):
        harvester = HarvesterFactory.create(name='Test Config')
        other = HarvesterFactory.create(name='Test Config Other')
        paths = MonitoredPathFactory.create_batch(size=3, harvester=harvester)
        MonitoredPathFactory.create_batch(size=3, harvester_id=other.uuid)
        url = reverse('harvester-config', args=(harvester.uuid,))
        headers = {'HTTP_AUTHORIZATION': f"Harvester {harvester.api_key}"}
        print("Test config rejection")
        self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)
        print("OK")
        print("Test access config")
        response = self.client.get(url, **headers)
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertIn('api_key', json)
        paths = [p.path for p in paths]
        for p in json['monitored_paths']:
            self.assertTrue(p['path'] in paths, "Unknown path reported in config")
            paths.remove(p['path'])
        self.assertEqual(len(paths), 0, "Not all monitored_paths reported in config")
        print("OK")
        print("Test config rejection with other harvester key")
        headers = {'HTTP_AUTHORIZATION': f"Harvester {other.api_key}"}
        self.assertEqual(self.client.get(url, **headers).status_code, status.HTTP_401_UNAUTHORIZED)
        print("OK")

    def test_view_access(self):
        harvester = HarvesterFactory.create(name='Test Update')
        user = UserFactory.create()
        user.groups.add(harvester.admin_group)
        user_header = self.get_token_header_for_user(user)
        other_user = UserFactory.create()
        other_user_header = self.get_token_header_for_user(other_user)
        self.client.force_login(user)
        url = reverse('harvester-list')
        print("Test only owner sees the harvester")
        list_a = [h['uuid'] for h in self.client.get(url, **user_header).json()]
        self.client.force_login(other_user)
        list_b = [h['uuid'] for h in self.client.get(url, **other_user_header).json()]
        self.assertIn(str(harvester.uuid), list_a)
        self.assertNotIn(str(harvester.uuid), list_b)
        print("OK")

    def test_update(self):
        harvester = HarvesterFactory.create(name='Test Update')
        user = UserFactory.create()
        self.client.force_login(user)
        user_header = self.get_token_header_for_user(user)
        other = HarvesterFactory.create(name='Test Update Other')
        url = reverse('harvester-detail', args=(harvester.uuid,))
        print("Test nonmember access")
        self.assertEqual(self.client.get(url, **user_header).status_code, status.HTTP_404_NOT_FOUND)
        print("OK")
        print("Test edit access rejection")
        self.assertEqual(
            self.client.patch(url, {'name': 'hacker'}, **user_header).status_code,
            status.HTTP_404_NOT_FOUND
        )
        print("OK")
        user.groups.add(harvester.admin_group)
        print("Test name duplication error")
        response = self.client.patch(url, {'name': other.name}, **user_header)
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)
        print("OK")
        print("Test successful update")
        t = harvester.sleep_time + 10
        n = harvester.name + " the Second"
        response = self.client.patch(url, {'name': n, 'sleep_time': t}, **user_header)
        harvester_updated = Harvester.objects.get(uuid=harvester.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "HTTP response error")
        self.assertEqual(harvester_updated.name, n, "name not updated")
        self.assertEqual(harvester_updated.sleep_time, t, "sleep_time not updated")
        print("OK")

    def test_envvars(self):
        def get_envvars(url: str, **kwargs) -> dict[str, str]:
            response = self.client.get(url, **kwargs)
            return response.json()['environment_variables']

        envvars = {'ABC_ONE': '17224', 'BBC_TWO': 'Quizzes and documentaries'}
        harvester = HarvesterFactory.create(name='Test Update')
        user = UserFactory.create()
        user_header = self.get_token_header_for_user(user)
        user.groups.add(harvester.admin_group)
        other_user = UserFactory.create()
        other_user_header = self.get_token_header_for_user(other_user)
        self.client.force_login(user)
        url = reverse('harvester-detail', args=(harvester.uuid,))
        print("Test envvars blank")
        self.assertDictEqual(get_envvars(url, **user_header), {})
        print("OK")
        print("Test add envvars")
        self.assertEqual(
            self.client.patch(url, {'environment_variables': envvars}, format='json', **user_header).status_code,
            status.HTTP_200_OK
        )
        self.assertDictEqual(get_envvars(url, **user_header), envvars)
        print("OK")
        print("Test harvester not show to unauthorized users")
        self.client.force_login(other_user)
        response = self.client.get(reverse('harvester-list'), **other_user_header)
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertNotIn(harvester.uuid, [h['uuid'] for h in json])
        for h in json:
            self.assertDictEqual(h['environment_variables'], {})
        print("OK")
        print("Test mark envvars deleted")
        self.client.force_login(user)
        self.assertEqual(
            self.client.patch(url, {'environment_variables': {}}, format='json', **user_header).status_code,
            status.HTTP_200_OK
        )
        self.assertDictEqual(get_envvars(url, **user_header), {})
        self.assertEqual(
            HarvesterEnvVar.objects.filter(harvester=harvester, deleted=True).count(),
            len(envvars.keys())
        )
        print("OK")

    def test_report(self):
        harvester = HarvesterFactory.create(name='Test Report')
        paths = MonitoredPathFactory.create_batch(size=2, harvester=harvester)
        url = reverse('harvester-report', args=(harvester.uuid,))
        headers = {'HTTP_AUTHORIZATION': f"Harvester {harvester.api_key}", 'format': 'json'}
        print("Test status missing")
        self.assertEqual(self.client.post(url, {}, **headers).status_code, status.HTTP_400_BAD_REQUEST)
        print("OK")
        print("Test path missing")
        self.assertEqual(
            self.client.post(url, {'status': 'success'}, **headers).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")
        print("Test path okay")
        path = paths[0].path
        self.assertEqual(
            self.client.post(
                url,
                {'status': 'error', 'path': path + 'x/yz.ext', 'monitored_path_uuid': paths[0].uuid},
                **headers
            ).status_code,
            status.HTTP_200_OK
        )
        HarvestError.objects.get(harvester__uuid=harvester.uuid, file__path=path + 'x/yz.ext')
        print("OK")
        print("Test error with new file")
        response = self.client.post(
            url,
            {'status': 'error', 'error': 'test', 'path': path + '/new/file.ext', 'monitored_path_uuid': paths[0].uuid},
            **headers
        )
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        f = ObservedFile.objects.get(path=path + '/new/file.ext', harvester_id=harvester.uuid)
        HarvestError.objects.get(harvester__uuid=harvester.uuid, file__uuid=f.uuid)
        print("OK")
        print("Test error with existing file")
        response = self.client.post(
            url,
            {'status': 'error', 'error': 'test', 'path': path + '/new/file.ext', 'monitored_path_uuid': paths[0].uuid},
            **headers
        )
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            HarvestError.objects.all().count(),
            3
        )
        print("OK")
        print("Test unrecognised status")
        self.assertEqual(
            self.client.post(url, {'status': 'unknown', 'path': path}, **headers).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")
        print("Test task file_size")
        body = {
            'status': 'success',
            'monitored_path_uuid': paths[0].uuid,
            'path': '/a/new/file.ext',
            'content': {'task': 'file_size', 'size': 1024}
        }
        response = self.client.post(url, body, **headers)
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        f = ObservedFile.objects.get(path='/a/new/file.ext', harvester_id=harvester.uuid)
        self.assertEqual(f.state, FileState.GROWING)
        print("OK")
        print("Test task import begin")
        body['content'] = {
            'task': 'import',
            'status': 'begin',
            'test_date': 1024.0,
            'core_metadata': {
                'Machine Type': 'Test machine',
                'Dataset Name': 'Test dataset',
                'num_rows': 1024,
                'last_sample_no': 0
            },
            'extra_metadata': {}
        }
        response = self.client.post(url, body, **headers)
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['state'], FileState.IMPORTING)
        # d = Dataset.objects.get(file__id=f.id)
        # self.assertEqual(d.type, 'Test machine')
        print("OK")
        # Below skipped because PyCharm won't run fixtures startup script
        # print("Test task import in_progress")
        # body['content'] = {
        #     'task': 'import',
        #     'status': 'in_progress',
        #     'test_date': 1024.0,
        #     'data': [
        #         {'column_name': 'x', 'unit_id': 5, 'values': {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5}},
        #         {'column_name': 'y', 'unit_symbol': 'psx', 'values': {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5}},
        #         {'column_name': 'z', 'column_id': 1, 'values': {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5}}
        #     ]
        # }
        # response = self.client.post(url, body, **headers)
        # print(response.json())
        # assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        # cols = DataColumn.objects.filter(dataset__id=d.id)
        # self.assertEqual(cols.count(), 4)
        # for c in cols:
        #     self.assertEqual(TimeseriesDataInt.objects.filter(column_id=c.id).count(), 5)
        # print("OK")
        print("Test task import complete")
        body['content'] = {
            'task': 'import',
            'status': 'complete',
            'test_date': 1024.0
        }
        response = self.client.post(url, body, **headers)
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['state'], FileState.IMPORTED)
        print("OK")


if __name__ == '__main__':
    unittest.main()
