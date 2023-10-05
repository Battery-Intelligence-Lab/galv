# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

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
    edit_kwargs = {'name': 'updated_Test Harvester'}

    def setUp(self):
        super().setUp()
        self.harvester = HarvesterFactory.create(name='Test Harvester', lab=self.lab)
        self.other_harvester = HarvesterFactory.create(name='Other Harvester', lab=self.lab)

    def test_create_unauthorised(self):
        for i, login in enumerate([
            lambda: self.client.force_authenticate(self.user),
            lambda: self.client.force_authenticate(self.admin),
            lambda: self.client.logout()
        ]):
            login()
            url = reverse(f'{self.stub}-list')
            create_dict = self.dict_factory(lab={'id': self.lab}, name=f'create_unauth_Harvester {i}')
            response = self.client.post(url, create_dict, format='json')
            assert_response_property(
                self, response, self.assertGreaterEqual, response.status_code,
                400, msg=f"Check can't create Harvester on {self.lab}[login{i}]"
            )

    def test_cannot_create_in_other_lab(self):
        self.client.force_authenticate(self.lab_admin)
        url = reverse(f'{self.stub}-list')
        create_dict = self.dict_factory(lab={'id': self.strange_lab.id}, name=f'create_badlab_Harvester')
        response = self.client.post(url, create_dict, format='json')
        assert_response_property(
            self, response, self.assertEqual, response.status_code,
            403, msg=f"Check {self.lab_admin.username} cannot create Harvester on {self.strange_lab}"
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

    def test_config_rejection(self):
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

    def test_harvester_endpoints_rejection(self):
        for token in [
            'bad_token',
            self.other_harvester.api_key
        ]:
            for target in ['config', 'report']:
                with self.subTest(token=token, target=target):
                    self.client.force_authenticate(token=f'Harvester {token}')
                    url = reverse(f'{self.stub}-{target}', args=(self.harvester.uuid,))
                    response = self.client.get(url)
                    assert_response_property(
                        self, response, self.assertEqual, response.status_code,
                        403, msg=f"Check can't access harvester {target} with token {token}"
                    )

    def test_harvester_endpoints(self):
        for target in ['config', 'report']:
            with self.subTest(target=target):
                self.client.force_authenticate(token=f'Harvester {self.harvester.api_key}')
                url = reverse(f'{self.stub}-{target}', args=(self.harvester.uuid,))
                response = self.client.get(url)
                assert_response_property(
                    self, response, self.assertEqual, response.status_code,
                    200, msg=f"Check harvester can access own {target}"
                )

    #
    # def test_view_access(self):
    #     harvester = HarvesterFactory.create(name='Test Update')
    #     user = UserFactory.create()
    #     user.groups.add(harvester.admin_group)
    #     user_header = self.get_token_header_for_user(user)
    #     other_user = UserFactory.create()
    #     other_user_header = self.get_token_header_for_user(other_user)
    #     self.client.force_login(user)
    #     url = reverse('harvester-list')
    #     print("Test only owner sees the harvester")
    #     list_a = [h['uuid'] for h in self.client.get(url, **user_header).json()]
    #     self.client.force_login(other_user)
    #     list_b = [h['uuid'] for h in self.client.get(url, **other_user_header).json()]
    #     self.assertIn(str(harvester.uuid), list_a)
    #     self.assertNotIn(str(harvester.uuid), list_b)
    #     print("OK")
    #
    # def test_update(self):
    #     harvester = HarvesterFactory.create(name='Test Update')
    #     user = UserFactory.create()
    #     self.client.force_login(user)
    #     user_header = self.get_token_header_for_user(user)
    #     other = HarvesterFactory.create(name='Test Update Other')
    #     url = reverse('harvester-detail', args=(harvester.uuid,))
    #     print("Test nonmember access")
    #     self.assertEqual(self.client.get(url, **user_header).status_code, status.HTTP_404_NOT_FOUND)
    #     print("OK")
    #     print("Test edit access rejection")
    #     self.assertEqual(
    #         self.client.patch(url, {'name': 'hacker'}, **user_header).status_code,
    #         status.HTTP_404_NOT_FOUND
    #     )
    #     print("OK")
    #     user.groups.add(harvester.admin_group)
    #     print("Test name duplication error")
    #     response = self.client.patch(url, {'name': other.name}, **user_header)
    #     assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_400_BAD_REQUEST)
    #     print("OK")
    #     print("Test successful update")
    #     t = harvester.sleep_time + 10
    #     n = harvester.name + " the Second"
    #     response = self.client.patch(url, {'name': n, 'sleep_time': t}, **user_header)
    #     harvester_updated = Harvester.objects.get(uuid=harvester.uuid)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK, "HTTP response error")
    #     self.assertEqual(harvester_updated.name, n, "name not updated")
    #     self.assertEqual(harvester_updated.sleep_time, t, "sleep_time not updated")
    #     print("OK")
    #
    # def test_envvars(self):
    #     def get_envvars(url: str, **kwargs) -> dict[str, str]:
    #         response = self.client.get(url, **kwargs)
    #         return response.json()['environment_variables']
    #
    #     envvars = {'ABC_ONE': '17224', 'BBC_TWO': 'Quizzes and documentaries'}
    #     harvester = HarvesterFactory.create(name='Test Update')
    #     user = UserFactory.create()
    #     user_header = self.get_token_header_for_user(user)
    #     user.groups.add(harvester.admin_group)
    #     other_user = UserFactory.create()
    #     other_user_header = self.get_token_header_for_user(other_user)
    #     self.client.force_login(user)
    #     url = reverse('harvester-detail', args=(harvester.uuid,))
    #     print("Test envvars blank")
    #     self.assertDictEqual(get_envvars(url, **user_header), {})
    #     print("OK")
    #     print("Test add envvars")
    #     self.assertEqual(
    #         self.client.patch(url, {'environment_variables': envvars}, format='json', **user_header).status_code,
    #         status.HTTP_200_OK
    #     )
    #     self.assertDictEqual(get_envvars(url, **user_header), envvars)
    #     print("OK")
    #     print("Test harvester not show to unauthorized users")
    #     self.client.force_login(other_user)
    #     response = self.client.get(reverse('harvester-list'), **other_user_header)
    #     assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
    #     json = response.json()
    #     self.assertNotIn(harvester.uuid, [h['uuid'] for h in json])
    #     for h in json:
    #         self.assertDictEqual(h['environment_variables'], {})
    #     print("OK")
    #     print("Test mark envvars deleted")
    #     self.client.force_login(user)
    #     self.assertEqual(
    #         self.client.patch(url, {'environment_variables': {}}, format='json', **user_header).status_code,
    #         status.HTTP_200_OK
    #     )
    #     self.assertDictEqual(get_envvars(url, **user_header), {})
    #     self.assertEqual(
    #         HarvesterEnvVar.objects.filter(harvester=harvester, deleted=True).count(),
    #         len(envvars.keys())
    #     )
    #     print("OK")
    #
    # def test_report(self):
    #     harvester = HarvesterFactory.create(name='Test Report')
    #     paths = MonitoredPathFactory.create_batch(size=2, harvester=harvester)
    #     url = reverse('harvester-report', args=(harvester.uuid,))
    #     headers = {'HTTP_AUTHORIZATION': f"Harvester {harvester.api_key}", 'format': 'json'}
    #     print("Test status missing")
    #     self.assertEqual(self.client.post(url, {}, **headers).status_code, status.HTTP_400_BAD_REQUEST)
    #     print("OK")
    #     print("Test path missing")
    #     self.assertEqual(
    #         self.client.post(url, {'status': 'success'}, **headers).status_code,
    #         status.HTTP_400_BAD_REQUEST
    #     )
    #     print("OK")
    #     print("Test path okay")
    #     path = paths[0].path
    #     self.assertEqual(
    #         self.client.post(
    #             url,
    #             {'status': 'error', 'path': path + 'x/yz.ext', 'monitored_path_uuid': paths[0].uuid},
    #             **headers
    #         ).status_code,
    #         status.HTTP_200_OK
    #     )
    #     HarvestError.objects.get(harvester__uuid=harvester.uuid, file__path=path + 'x/yz.ext')
    #     print("OK")
    #     print("Test error with new file")
    #     response = self.client.post(
    #         url,
    #         {'status': 'error', 'error': 'test', 'path': path + '/new/file.ext', 'monitored_path_uuid': paths[0].uuid},
    #         **headers
    #     )
    #     assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
    #     f = ObservedFile.objects.get(path=path + '/new/file.ext', harvester_id=harvester.uuid)
    #     HarvestError.objects.get(harvester__uuid=harvester.uuid, file__uuid=f.uuid)
    #     print("OK")
    #     print("Test error with existing file")
    #     response = self.client.post(
    #         url,
    #         {'status': 'error', 'error': 'test', 'path': path + '/new/file.ext', 'monitored_path_uuid': paths[0].uuid},
    #         **headers
    #     )
    #     assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(
    #         HarvestError.objects.all().count(),
    #         3
    #     )
    #     print("OK")
    #     print("Test unrecognised status")
    #     self.assertEqual(
    #         self.client.post(url, {'status': 'unknown', 'path': path}, **headers).status_code,
    #         status.HTTP_400_BAD_REQUEST
    #     )
    #     print("OK")
    #     print("Test task file_size")
    #     body = {
    #         'status': 'success',
    #         'monitored_path_uuid': paths[0].uuid,
    #         'path': '/a/new/file.ext',
    #         'content': {'task': 'file_size', 'size': 1024}
    #     }
    #     response = self.client.post(url, body, **headers)
    #     assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
    #     f = ObservedFile.objects.get(path='/a/new/file.ext', harvester_id=harvester.uuid)
    #     self.assertEqual(f.state, FileState.GROWING)
    #     print("OK")
    #     print("Test task import begin")
    #     body['content'] = {
    #         'task': 'import',
    #         'status': 'begin',
    #         'test_date': 1024.0,
    #         'core_metadata': {
    #             'Machine Type': 'Test machine',
    #             'Dataset Name': 'Test dataset',
    #             'num_rows': 1024,
    #             'last_sample_no': 0
    #         },
    #         'extra_metadata': {}
    #     }
    #     response = self.client.post(url, body, **headers)
    #     assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.json()['state'], FileState.IMPORTING)
    #     # d = Dataset.objects.get(file__id=f.id)
    #     # self.assertEqual(d.type, 'Test machine')
    #     print("OK")
    #     # Below skipped because PyCharm won't run fixtures startup script
    #     # print("Test task import in_progress")
    #     # body['content'] = {
    #     #     'task': 'import',
    #     #     'status': 'in_progress',
    #     #     'test_date': 1024.0,
    #     #     'data': [
    #     #         {'column_name': 'x', 'unit_id': 5, 'values': {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5}},
    #     #         {'column_name': 'y', 'unit_symbol': 'psx', 'values': {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5}},
    #     #         {'column_name': 'z', 'column_id': 1, 'values': {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5}}
    #     #     ]
    #     # }
    #     # response = self.client.post(url, body, **headers)
    #     # print(response.json())
    #     # assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
    #     # cols = DataColumn.objects.filter(dataset__id=d.id)
    #     # self.assertEqual(cols.count(), 4)
    #     # for c in cols:
    #     #     self.assertEqual(TimeseriesDataInt.objects.filter(column_id=c.id).count(), 5)
    #     # print("OK")
    #     print("Test task import complete")
    #     body['content'] = {
    #         'task': 'import',
    #         'status': 'complete',
    #         'test_date': 1024.0
    #     }
    #     response = self.client.post(url, body, **headers)
    #     assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.json()['state'], FileState.IMPORTED)
    #     print("OK")


if __name__ == '__main__':
    unittest.main()
