# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
from django.urls import reverse
from rest_framework import status
import logging

from backend.backend_django.galv.tests.utils import assert_response_property, APITestCase
from .factories import UserFactory, LabFactory, TeamFactory
from django.contrib.auth.models import User

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


"""
* Anonymous users can create a new user
* Users can view and update their own details
* Users can view any user's details with whom they share a lab
* Lab admins can view any user's details
"""

stub = 'userproxy'

class UserTests(APITestCase):
    def setUp(self):
        self.non_user = UserFactory.create(username='test_users', is_active=True)
        self.user = UserFactory.create(username='test_users_user', is_active=True)

    def test_list(self):
        """
        * Users can view any user's details with whom they share a lab
        * Lab admins can view any user's details
        """
        lab = LabFactory.create()
        lab_team = TeamFactory.create(lab=lab)
        strange_lab = LabFactory.create()
        strange_lab_team = TeamFactory.create(lab=strange_lab)
        admin = UserFactory.create(username='test_list_admin')
        lab.admin_group.user_set.add(admin)
        strange_admin = UserFactory.create(username='test_list_strange_admin')
        strange_lab.admin_group.user_set.add(strange_admin)
        user = UserFactory.create(username='test_list_user')
        lab_team.member_group.user_set.add(user)
        colleague = UserFactory.create(username='test_list_colleague')
        lab_team.member_group.user_set.add(colleague)
        stranger = UserFactory.create(username='test_list_stranger')
        strange_lab_team.member_group.user_set.add(stranger)
        mystery_guest = UserFactory.create(username='test_list_mystery_guest')
        lab.admin_group.save()
        strange_lab.admin_group.save()
        lab_team.member_group.save()
        strange_lab_team.member_group.save()

        def assert_user_list(viewing_user, expected_contents):
            self.client.force_authenticate(viewing_user)
            result = self.client.get(reverse(f'{stub}-list'))
            assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_200_OK)
            expected_contents = [u.username for u in expected_contents]
            contents = [u['username'] for u in result.json()]
            self.assertCountEqual(contents, expected_contents)
            for u in expected_contents:
                self.assertIn(u, contents)
            return result

        print("Test list users (anonymous)")
        result = self.client.get(reverse(f'{stub}-list'))
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_401_UNAUTHORIZED)
        print("OK")
        print("Test list users (user)")
        assert_user_list(user, [user, colleague, admin])
        print("OK")
        print("Test list users (admin)")
        assert_user_list(admin, [user, colleague, admin, stranger, strange_admin, mystery_guest, self.user, self.non_user])
        print("OK")
        print("Test list users (mystery guest)")
        assert_user_list(mystery_guest, [])
        print("OK")

    def test_create(self):
        """
        * Anonymous users can create a new user
        * Users can view and update their own details
        """
        url = reverse(f'{stub}-list')
        data = {'username': 'new_user'}
        print("Test Create User rejection (no username)")
        self.assertEqual(
            self.client.post(url, {}).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")
        print("Test Create User rejection (no password)")
        self.assertEqual(
            self.client.post(url, data).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")
        data['password'] = 'pw'
        print("Test Create User rejection (no email)")
        self.assertEqual(
            self.client.post(url, data).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")
        data['email'] = 'x@example.com'
        print("Test Create User rejection (short password)")
        self.assertEqual(
            self.client.post(url, data).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")
        data['password'] = 'password'
        print("Test Create User rejection (username in use)")
        self.assertEqual(
            self.client.post(url, {**data, 'username': self.non_user.username}).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")
        print("Test Create User success")
        response = self.client.post(url, data)
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['username'], data['username'])
        print("Attempting login")
        response_user = response.json()
        self.client.force_authenticate(User.objects.get(id=response_user['id']))
        self.assertEqual(self.client.get(response_user['url']).status_code, status.HTTP_200_OK)
        print("OK")

    def test_update(self):
        """
        * Users can view and update their own details
        """
        url = reverse(f'{stub}-detail', args=(self.user.id,))
        print("Test update rejected (no current password)")
        self.client.force_authenticate(self.user)
        body = {'email': 'test.user@example.com', 'password': 'complex_password'}
        self.assertEqual(
            self.client.patch(url, body).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")
        print("Test update rejected (no access to others)")
        body['current_password'] = 'password'
        self.user.set_password(body['current_password'])
        self.user.save()
        self.assertEqual(
            self.client.patch(reverse(f'{stub}-detail', args=(self.non_user.id,)), body).status_code,
            status.HTTP_403_FORBIDDEN
        )
        print("OK")
        print("Test update rejected (invalid email)")
        self.assertEqual(
            self.client.patch(url, {**body, 'email': 'bad-email'}).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")
        print("Test update okay")
        response = self.client.patch(url, body)
        json = response.json()
        assert_response_property(self, response, self.assertEqual, response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['email'], body['email'])
        self.assertTrue(User.objects.get(id=self.user.id).check_password(body['password']))
        print("OK")


if __name__ == '__main__':
    unittest.main()
