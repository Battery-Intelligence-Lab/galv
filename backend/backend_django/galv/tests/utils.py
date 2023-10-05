# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import base64
import os
from unittest import SkipTest

from django.core.files.storage import FileSystemStorage
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from backend.backend_django.galv.tests.factories import LabFactory, TeamFactory, UserFactory, generate_create_dict


def assert_response_property(self, response, assertion, *args, **kwargs):
    try:
        assertion(*args, **kwargs)
    except AssertionError as e:
        raise AssertionError(f"{e}\nResponse: {response.json()}")


class GalvTestCase(APITestCase):
    edit_kwargs = None  # a dict of kwargs to send to update calls. Can be overriden with self.get_edit_kwargs()
    stub = None  # the stub name of the resource, e.g. 'cell'
    factory = None  # the factory for creating resources

    def __init__(self, *args, **kwargs):
        abstract = self.__class__.__name__ == 'GalvTestCase' or kwargs.pop('abstract', False)
        super().__init__(*args, **kwargs)
        self.create_resource_users_run = False
        if abstract:
            return
        if self.edit_kwargs is None and type(self).get_edit_kwargs == GalvTeamResourceTestCase.get_edit_kwargs:
            raise AssertionError(f"Children of {self.__class__.__name__} must define self.edit_kwargs or self.get_edit_kwargs()")
        if self.stub is None:
            raise AssertionError(f"Children of {self.__class__.__name__} must define a self.stub")
        if self.factory is None:
            raise AssertionError(f"Children of {self.__class__.__name__} must define a self.factory")
        self.dict_factory = generate_create_dict(self.factory)

    def get_edit_kwargs(self):
        """
        Return the kwargs to send to update calls.
        """
        return self.edit_kwargs

    def get_create_kwargs(self):
        """
        Return the kwargs to send to create calls.

        This method will create a new object as a stub and create dependents as real database entries.
        """
        new_resource = self.factory.create()
        new_resource_dict = new_resource.to_dict()
        new_resource.delete()
        return new_resource_dict

    def setUp(self) -> None:
        super().setUp()
        if self.__class__.__name__ == 'GalvTestCase':
            raise self.skipTest("This is an abstract base class")
        self.create_resource_users()

    def create_resource_users(self) -> None:
        """
        Create users and resources for testing access to resources.
        Of particular note, this creates a self.user and self.admin
        who are member/admin in self.lab_team.
        """
        if getattr(self, 'create_resource_users_run', False):
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


@override_settings(MEDIA_ROOT='/tmp')
class GalvTeamResourceTestCase(GalvTestCase):
    """
    This class provides a set of methods for testing access to resources.
    It has convenience methods for creating users and resources, and for creating
    tests for access to those resources.

    It comes packaged with CRUD tests for the resource,
    tested against several different user profiles.

    Children should define:
    - self.factory: the factory for creating resources
    - self.stub: the stub name of the resource for URL lookups, e.g. 'cell'
    - self.get_edit_kwargs(): the kwargs to send to update calls

    Access is governed by a waterfall model such that the most open criterion
    is tested first.
    The access is tested in this order:
    * Create requests allowed if:
        * user is a member of the team
    * Read requests allowed if any of:
        * anonymous_can_read=True
        * any_user_can_read=True and user is in a lab
        * lab_members_can_read and user is in Team's Lab
        * user is a member of the team
    * Write requests allowed if any of:
        * any_user_can_write=True and user is in a lab
        * lab_members_can_edit and user is in Team's Lab
        * team_members_can_edit=True and user is a member of the team
        * user is an admin of the team
    * Delete requests allowed if:
        * user is a member of the team
    """
    def __init__(self, *args, **kwargs):
        abstract = self.__class__.__name__ == 'GalvTeamResourceTestCase'
        super().__init__(*args, **kwargs, abstract=abstract)
        self.create_test_resources_run = False

    def get_create_kwargs(self):
        """
        Return the kwargs to send to create calls.

        This method will create a new object as a stub and create dependents as real database entries.
        """
        new_resource = self.factory.create(team=self.lab_team)
        new_resource_dict = new_resource.to_dict()
        new_resource.delete()
        return new_resource_dict

    def create_with_perms(self, **perms):
        # Pass team prop to the correct object
        # if self.factory.__name__ in ['CellFactory', 'EquipmentFactory', 'ScheduleFactory']:
        #     return self.factory.create(family__team=self.lab_team, **perms)
        return self.factory.create(team=self.lab_team, **perms)

    def create_test_resources(self):
        """
        Helper method for creating access test resources.
        """
        if getattr(self, 'create_test_resources_run', False):
            return

        self.access_test_default = self.create_with_perms()
        self.access_test_team_no_write = self.create_with_perms(
            team_members_can_edit=False,
            team_members_can_delete=False
        )
        self.access_test_lab_no_read = self.create_with_perms(lab_members_can_read=False)
        self.access_test_lab_write = self.create_with_perms(lab_members_can_edit=True)
        self.access_test_authorised_read = self.create_with_perms(any_user_can_read=True)
        self.access_test_authorised_write = self.create_with_perms(any_user_can_edit=True)
        self.access_test_open = self.create_with_perms(anonymous_can_read=True)

        self.create_test_resources_run = True

    def get_resource_description(self, resource):
        if resource == self.access_test_default:
            return "default"
        elif resource == self.access_test_team_no_write:
            return "team_no_write"
        elif resource == self.access_test_lab_no_read:
            return "lab_no_read"
        elif resource == self.access_test_lab_write:
            return "lab_write"
        elif resource == self.access_test_authorised_read:
            return "authorised_read"
        elif resource == self.access_test_authorised_write:
            return "authorised_write"
        elif resource == self.access_test_open:
            return "open"
        return "unknown"

    def setUp(self) -> None:
        super().setUp()
        if self.__class__.__name__ == 'GalvTeamResourceTestCase':
            raise self.skipTest("This is an abstract base class")
        self.create_test_resources()

    def file_safe_request(self, request_method, url, content, **kwargs):
        """
        Helper method for making requests with file content.
        """
        return_value = None
        if 'schedule_file' in content:
            return_value = request_method(url, content, **kwargs)
        else:
            return_value = request_method(url, content, **{'format': 'json', **kwargs})
        return return_value

    def test_create_non_team_member(self):
        """
        * Create requests disallowed
        """
        for user, login in {
            'lab_admin': lambda: self.client.force_authenticate(self.lab_admin),
            'strange_lab_admin': lambda: self.client.force_authenticate(self.strange_lab_admin),
            'anonymous': lambda: self.client.logout()
        }.items():
            with self.subTest(user=user):
                login()
                url = reverse(f'{self.stub}-list')
                create_dict = self.dict_factory(team={'name': self.lab_team.name, 'lab': self.lab_team.lab})
                response = self.file_safe_request(self.client.post, url, create_dict)
                assert_response_property(
                    self, response, self.assertGreaterEqual, response.status_code,
                    400, msg=f"Check can't create resources on {self.lab_team}"
                )

    def test_create_team_member(self):
        """
        * Create requests allowed if:
            * user is a member of the team
        """
        for user in [self.admin, self.user]:
            with self.subTest(username=user.username):
                self.client.force_authenticate(user)
                url = reverse(f'{self.stub}-list')
                create_dict = self.dict_factory(team={'name': self.lab_team.name, 'lab': self.lab_team.lab})
                response = self.file_safe_request(self.client.post, url, create_dict)
                assert_response_property(
                    self, response, self.assertEqual, response.status_code,
                    201, msg=f"Check {user.username} can create resources on {self.lab_team}"
                )

    def test_read_anonymous(self):
        """
        * Read requests allowed if any of:
            * anonymous_can_read=True
        """
        self.client.logout()
        response = self.client.get(reverse(f'{self.stub}-list'))
        assert_response_property(self, response, self.assertEqual, response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertResourceInResult(self.access_test_open, response)

    def test_read_authorised(self):
        """
        * Read requests allowed if any of:
            * anonymous_can_read=True
            * any_user_can_read=True and user is in a lab
        """
        self.client.force_authenticate(self.strange_lab_admin)
        response = self.client.get(reverse(f'{self.stub}-list'))
        assert_response_property(self, response, self.assertEqual, response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        self.assertResourceInResult(self.access_test_open, response)
        self.assertResourceInResult(self.access_test_authorised_read, response)
        self.assertResourceInResult(self.access_test_authorised_write, response)

    def test_read_lab_member(self):
        """
        * Read requests allowed if any of:
            * anonymous_can_read=True
            * any_user_can_read=True and user is in a lab
            * lab_members_can_read and user is in Team's Lab
        """
        self.client.force_authenticate(self.lab_admin)
        response = self.client.get(reverse(f'{self.stub}-list'))
        assert_response_property(self, response, self.assertEqual, response.status_code, 200)
        self.assertEqual(len(response.json()), 6)
        for resource in [
            self.access_test_open,
            self.access_test_authorised_read,
            self.access_test_authorised_write,
            self.access_test_default,
            self.access_test_lab_write,
            self.access_test_team_no_write
        ]:
            self.assertResourceInResult(resource, response)


    def test_read_team_member(self):
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
            self.assertEqual(len(response.json()), 7)
            for resource in [
                self.access_test_open,
                self.access_test_authorised_read,
                self.access_test_authorised_write,
                self.access_test_default,
                self.access_test_lab_write,
                self.access_test_team_no_write,
                self.access_test_lab_no_read
            ]:
                self.assertResourceInResult(resource, response)

    def test_update_anonymous(self):
        """
        * Write requests disallowed
        """
        self.client.logout()
        for resource in [
            self.access_test_default,
            self.access_test_team_no_write,
            self.access_test_lab_no_read,
            self.access_test_lab_write,
            self.access_test_authorised_read,
            self.access_test_authorised_write,
            self.access_test_open
        ]:
            with self.subTest(resource=self.get_resource_description(resource)):
                url = reverse(f'{self.stub}-detail', args=(resource.pk,))
                response = self.file_safe_request(self.client.patch, url, self.get_edit_kwargs())
                assert_response_property(self, response, self.assertEqual, response.status_code,
                                         401, msg=f"Check anonymous can't update resources on {self.lab_team}")


    def test_update_authorised(self):
        """
        * Write requests allowed if any of:
            * any_user_can_write=True and user is in a lab
        """
        self.client.force_authenticate(self.strange_lab_admin)
        for resource, code in [
            (self.access_test_default, 403),
            (self.access_test_team_no_write, 403),
            (self.access_test_authorised_read, 403),
            (self.access_test_authorised_write, 200),
            (self.access_test_lab_no_read, 403),
            (self.access_test_lab_write, 403),
            (self.access_test_open, 403)
        ]:
            with self.subTest(resource=self.get_resource_description(resource)):
                url = reverse(f'{self.stub}-detail', args=(resource.pk,))
                response = self.file_safe_request(self.client.patch, url, self.get_edit_kwargs())
                assert_response_property(
                    self, response, self.assertEqual, response.status_code,
                    code, msg=f"Check {self.strange_lab_admin.username} gets HTTP {code} on {resource} [got {response.status_code} instead]"
                )
    def test_update_lab_member(self):
        """
        * Write requests allowed if any of:
            * any_user_can_write=True and user is in a lab
            * lab_members_can_edit and user is in Team's Lab
        """
        self.client.force_authenticate(self.lab_admin)
        for resource, code in [
            (self.access_test_default, 403),
            (self.access_test_team_no_write, 403),
            (self.access_test_authorised_read, 403),
            (self.access_test_authorised_write, 200),
            (self.access_test_lab_no_read, 403),
            (self.access_test_lab_write, 200),
            (self.access_test_open, 403)
        ]:
            with self.subTest(resource=self.get_resource_description(resource)):
                url = reverse(f'{self.stub}-detail', args=(resource.pk,))
                response = self.file_safe_request(self.client.patch, url, self.get_edit_kwargs())
                assert_response_property(
                    self, response, self.assertEqual, response.status_code,
                    code, msg=f"Check {self.lab_admin.username} gets HTTP {code} on {resource} [got {response.status_code} instead]"
                )

    def test_update_team_member(self):
        """
        * Write requests allowed if any of:
            * any_user_can_write=True and user is in a lab
            * team_members_can_edit=True and user is a member of the team
        """
        self.client.force_authenticate(self.user)
        for resource, code in [
            (self.access_test_default, 200),
            (self.access_test_team_no_write, 403),
            (self.access_test_lab_no_read, 200),
            (self.access_test_lab_write, 200),
            (self.access_test_authorised_read, 200),
            (self.access_test_authorised_write, 200),
            (self.access_test_open, 200)
        ]:
            with self.subTest(resource=self.get_resource_description(resource)):
                url = reverse(f'{self.stub}-detail', args=(resource.pk,))
                response = self.file_safe_request(self.client.patch, url, self.get_edit_kwargs())
                assert_response_property(self, response, self.assertEqual, response.status_code, code)

    def test_update_team_admin(self):
        """
        * Write requests allowed if any of:
            * any_user_can_write=True and user is in a lab
            * team_members_can_edit=True and user is a member of the team
            * user is an admin of the team
        """
        self.client.force_authenticate(self.admin)
        for resource in [
            self.access_test_default,
            self.access_test_team_no_write,
            self.access_test_lab_no_read,
            self.access_test_lab_write,
            self.access_test_authorised_read,
            self.access_test_authorised_write,
            self.access_test_open
        ]:
            with self.subTest(resource=self.get_resource_description(resource)):
                url = reverse(f'{self.stub}-detail', args=(resource.pk,))
                response = self.file_safe_request(self.client.patch, url, self.get_edit_kwargs())
                assert_response_property(self, response, self.assertEqual, response.status_code, 200)

    def test_destroy_non_team_member(self):
        """
        * Delete requests disallowed
        """
        for user, login in {
            'lab_admin': lambda: self.client.force_authenticate(self.lab_admin),
            'strange_lab_admin': lambda: self.client.force_authenticate(self.strange_lab_admin),
            'anonymous': lambda: self.client.logout()
        }.items():
            for perms, code in [
                ({'team_members_can_delete': True}, 403 if user != 'anonymous' else 401),
                ({'team_members_can_delete': False}, 403 if user != 'anonymous' else 401)
            ]:
                with self.subTest(user=user, perms=perms):
                    login()
                    resource = self.create_with_perms(**perms)
                    url = reverse(f'{self.stub}-detail', args=(resource.pk,))
                    response = self.client.delete(url)
                    assert_response_property(
                        self, response, self.assertEqual, response.status_code,
                        code, msg=f"Check can't delete resources on {self.lab_team}"
                    )

    def test_destroy_team_member(self):
        """
        * Delete requests allowed if:
            * user is a member of the team
        """
        for user in [self.admin, self.user]:
            for perms, code in [
                ({'team_members_can_delete': True}, 204),
                ({'team_members_can_delete': False}, 204 if user == self.admin else 403)
            ]:
                with self.subTest(username=user.username, perms=perms):
                    self.client.force_authenticate(user)
                    resource = self.create_with_perms(**perms)
                    url = reverse(f'{self.stub}-detail', args=(resource.pk,))
                    response = self.client.delete(url)
                    assert_response_property(self, response, self.assertEqual, response.status_code,
                                             code, msg=f"Check {user.username} gets {code} deleting resources on {self.lab_team}")
