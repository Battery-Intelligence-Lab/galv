# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import base64
from unittest import SkipTest

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from backend.backend_django.galv.tests.factories import LabFactory, TeamFactory, UserFactory, generate_dict_factory


def assert_response_property(self, response, assertion, *args, **kwargs):
    try:
        assertion(*args, **kwargs)
    except AssertionError as e:
        raise AssertionError(f"{e}\nResponse: {response.json()}")


class GalvTeamResourceTestCase(APITestCase):
    """
    This class provides a set of methods for testing access to resources.
    It has convenience methods for creating users and resources, and for creating
    tests for access to those resources.

    Access is governed by a waterfall model such that the most open criterion
    is tested first.
    The access is tested in this order:
    * Read requests allowed if any of:
        * anonymous_can_read=True
        * any_user_can_read=True and user is in a lab
        * user is a member of the team
    * Write requests allowed if any of:
        * any_user_can_write=True and user is in a lab
        * members_can_edit=True and user is a member of the team
        * user is an admin of the team
    * Create requests allowed if:
        * user is a member of the team
    """
    edit_kwargs = None
    stub = None
    factory = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_resource_users_run = False
        self.create_access_test_resources_run = False
        if self.__class__.__name__ == 'GalvTeamResourceTestCase':
            return
        if self.factory is None:
            raise AssertionError("Children of GalvTeamResourceTestCase must define a self.factory")
        if self.stub is None:
            raise AssertionError("Children of GalvTeamResourceTestCase must define a self.stub")
        if self.edit_kwargs is None:
            raise AssertionError("Children of GalvTeamResourceTestCase must define a self.edit_kwargs")
        self.dict_factory = generate_dict_factory(self.factory)

    def create_resource_users(self) -> None:
        """
        Create users and resources for testing access to resources.
        Of particular note, this creates a self.user and self.admin
        who are member/admin in self.lab_team.
        """
        if hasattr(self, 'create_resource_users_run') and self.create_resource_users_run:
            return

        prefix = self.stub

        self.lab = LabFactory.create(name=f'{prefix} Lab')
        self.lab_team = TeamFactory.create(name=f'{prefix} Lab Team', lab=self.lab)
        self.user = UserFactory.create(username=f'{prefix}_user')
        self.lab_team.member_group.user_set.add(self.user)
        self.admin = UserFactory.create(username=f'{prefix}_admin')
        self.lab_team.admin_group.user_set.add(self.admin)
        self.lab_admin = UserFactory.create(username=f'{prefix}_lab_admin')
        self.lab.admin_group.user_set.add(self.lab_admin)
        self.strange_lab = LabFactory.create(name=f'{prefix} Strange Lab')
        self.strange_lab_team = TeamFactory.create(name=f'{prefix} Strange Lab Team', lab=self.strange_lab)
        self.strange_lab_admin = UserFactory.create(username=f'{prefix}_strange_lab_admin')
        self.strange_lab.admin_group.user_set.add(self.strange_lab_admin)
        self.strange_lab_team.admin_group.user_set.add(self.strange_lab_admin)

        self.create_resource_users_run = True

    def create_access_test_resources(self):
        """
        Helper method for creating access test resources.
        """
        if hasattr(self, 'create_access_test_resources_run') and self.create_access_test_resources_run:
            return
        def create_with_perms(**perms):
            return self.factory.create(team=self.lab_team, **perms)

        self.access_test_default = create_with_perms()
        self.access_test_admin_only = create_with_perms(members_can_edit=False)
        self.access_test_authorised_read = create_with_perms(any_user_can_read=True)
        self.access_test_authorised_write = create_with_perms(any_user_can_edit=True)
        self.access_test_open = create_with_perms(anonymous_can_read=True)

        self.create_access_test_resources_run = True

    def assertResourceInResult(self, resource, result, assert_single_result=True, assert_reachable=True):
        json = result.json()
        if not len(json):
            raise AssertionError(f"Empty result when looking for {resource}")
        pk_field = 'id' if 'id' in json[0] else 'uuid'
        pk = resource.pk if pk_field == 'id' else str(resource.pk)
        matched_result = [r for r in json if r[pk_field] == pk]
        if assert_single_result and len(matched_result) != 1:
            raise AssertionError(f"Expected single instance of {resource}, got {len(matched_result)} instances")
        if not assert_reachable:
            return
        matched_result = matched_result[0]
        if 'url' not in matched_result:
            raise AssertionError(f"Result does not have a URL for {resource}")
        url = matched_result['url']
        result = self.client.get(url)
        if result.status_code < 200 or result.status_code >= 400:
            raise AssertionError(f"Could not reach {url} for {resource} (HTTP {result.status_code})")

    def setUp(self) -> None:
        if self.__class__.__name__ == 'GalvTeamResourceTestCase':
            raise self.skipTest("This is an abstract base class")
        self.create_resource_users()
        self.create_access_test_resources()

    def test_read_access_anonymous(self):
        """
        * Read requests allowed if any of:
            * anonymous_can_read=True
        """
        self.client.logout()
        response = self.client.get(reverse(f'{self.stub}-list'))
        assert_response_property(self, response, self.assertEqual, response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertResourceInResult(self.access_test_open, response)

    def test_read_access_authorised(self):
        """
        * Read requests allowed if any of:
            * anonymous_can_read=True
            * any_user_can_read=True and user is in a lab
        """
        for user in [self.strange_lab_admin, self.lab_admin]:
            self.client.force_authenticate(user)
            response = self.client.get(reverse(f'{self.stub}-list'))
            assert_response_property(self, response, self.assertEqual, response.status_code, 200)
            self.assertEqual(len(response.json()), 3)
            self.assertResourceInResult(self.access_test_open, response)
            self.assertResourceInResult(self.access_test_authorised_read, response)
            self.assertResourceInResult(self.access_test_authorised_write, response)


    def test_read_access_member(self):
        """
        * Read requests allowed if any of:
            * anonymous_can_read=True
            * any_user_can_read=True and user is in a lab
            * user is a member of the team
        """
        for user in [self.admin, self.user]:
            self.client.force_authenticate(user)
            response = self.client.get(reverse(f'{self.stub}-list'))
            assert_response_property(self, response, self.assertEqual, response.status_code, 200)
            self.assertEqual(len(response.json()), 5)
            self.assertResourceInResult(self.access_test_open, response)
            self.assertResourceInResult(self.access_test_authorised_read, response)
            self.assertResourceInResult(self.access_test_authorised_write, response)
            self.assertResourceInResult(self.access_test_default, response)
            self.assertResourceInResult(self.access_test_admin_only, response)

    def test_write_access_anonymous(self):
        """
        * Write requests disallowed
        """
        self.client.logout()
        for resource in [
            self.access_test_default,
            self.access_test_admin_only,
            self.access_test_authorised_read,
            self.access_test_authorised_write,
            self.access_test_open
        ]:
            url = reverse(f'{self.stub}-detail', args=(resource.pk,))
            response = self.client.patch(url, self.edit_kwargs)
            assert_response_property(self, response, self.assertEqual, response.status_code, 401)

    def test_write_access_authorised(self):
        """
        * Write requests allowed if any of:
            * any_user_can_write=True and user is in a lab
        """
        for user in [self.strange_lab_admin, self.lab_admin]:
            self.client.force_authenticate(user)
            for resource, code in [
                (self.access_test_default, 403),
                (self.access_test_admin_only, 403),
                (self.access_test_authorised_read, 403),
                (self.access_test_authorised_write, 200),
                (self.access_test_open, 403)
            ]:
                url = reverse(f'{self.stub}-detail', args=(resource.pk,))
                response = self.client.patch(url, self.edit_kwargs)
                assert_response_property(
                    self, response, self.assertEqual, response.status_code,
                    code, msg=f"Check {user.username} gets HTTP {code} on {resource} [got {response.status_code} instead]"
                )

    def test_write_access_member(self):
        """
        * Write requests allowed if any of:
            * any_user_can_write=True and user is in a lab
            * members_can_edit=True and user is a member of the team
        """
        self.client.force_authenticate(self.user)
        for resource, code in [
            (self.access_test_default, 200),
            (self.access_test_admin_only, 403),
            (self.access_test_authorised_read, 200),
            (self.access_test_authorised_write, 200),
            (self.access_test_open, 200)
        ]:
            url = reverse(f'{self.stub}-detail', args=(resource.pk,))
            response = self.client.patch(url, self.edit_kwargs)
            assert_response_property(self, response, self.assertEqual, response.status_code, code)

    def test_write_access_admin(self):
        """
        * Write requests allowed if any of:
            * any_user_can_write=True and user is in a lab
            * members_can_edit=True and user is a member of the team
            * user is an admin of the team
        """
        self.client.force_authenticate(self.admin)
        for resource in [
            self.access_test_default,
            self.access_test_admin_only,
            self.access_test_authorised_read,
            self.access_test_authorised_write,
            self.access_test_open
        ]:
            url = reverse(f'{self.stub}-detail', args=(resource.pk,))
            response = self.client.patch(url, self.edit_kwargs)
            assert_response_property(self, response, self.assertEqual, response.status_code, 200)

    def test_create_access_non_member(self):
        """
        * Create requests disallowed
        """
        for i, login in enumerate([
            lambda: self.client.force_authenticate(self.lab_admin),
            lambda: self.client.force_authenticate(self.strange_lab_admin),
            lambda: self.client.logout()
        ]):
            login()
            url = reverse(f'{self.stub}-list')
            create_dict = self.dict_factory(team=self.lab_team.id)
            response = self.client.post(url, create_dict, format='json')
            assert_response_property(
                self, response, self.assertGreaterEqual, response.status_code,
                400, msg=f"Check can't create resources on {self.lab_team}[login{i}]"
            )

    def test_create_access_member(self):
        """
        * Create requests allowed if:
            * user is a member of the team
        """
        for user in [self.admin, self.user]:
            self.client.force_authenticate(user)
            url = reverse(f'{self.stub}-list')
            create_dict = self.dict_factory(team=self.lab_team.id)
            response = self.client.post(url, create_dict, format='json')
            assert_response_property(
                self, response, self.assertEqual, response.status_code,
                201, msg=f"Check {user.username} can create resources on {self.lab_team}"
            )
