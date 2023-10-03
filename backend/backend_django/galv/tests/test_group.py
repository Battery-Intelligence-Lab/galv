# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import unittest
from django.urls import reverse
from rest_framework import status
import logging

from galv.models import Team
from backend.backend_django.galv.tests.utils import assert_response_property, APITestCase
from .factories import UserFactory, LabFactory, TeamFactory

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


"""
* Lab admins can create teams for their own lab
* Lab admins can add/remove users to/from their lab and its teams
    * Labs must have at least one admin
* Team admins can add/remove users to/from their team
* Lab members can view their lab
* Lab members can view their lab's teams
"""

stub = 'groupproxy'

class GroupTests(APITestCase):
    def setUp(self):
        self.lab = LabFactory.create(name='Test Lab')
        self.lab_team = TeamFactory.create(name='Test Lab Team', lab=self.lab)
        self.lab_other_team = TeamFactory.create(name='Test Lab Other Team', lab=self.lab)
        self.strange_lab = LabFactory.create(name='Strange Lab')
        self.admin = UserFactory.create(username='test_group_admin')
        self.lab.admin_group.user_set.add(self.admin)
        self.user = UserFactory.create(username='test_group_user')
        self.lab_team.member_group.user_set.add(self.user)
        self.colleague = UserFactory.create(username='test_group_colleague')
        self.lab_team.member_group.user_set.add(self.colleague)
        self.associate = UserFactory.create(username='test_group_associate')
        self.lab_other_team.member_group.user_set.add(self.associate)
        self.lab.admin_group.save()
        self.lab_team.member_group.save()

    def test_list_own_lab(self):
        """
        * Lab members can view their lab
        """
        self.client.force_authenticate(self.user)
        result = self.client.get(reverse(f'lab-list'))
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result.json()), 1)
        self.assertEqual(result.json()[0]['name'], self.lab.name)

    def test_list_own_lab_groups(self):
        """
        * Lab members can view their lab
        """
        self.client.force_authenticate(self.user)
        result = self.client.get(reverse(f'{stub}-list'))
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result.json()), 3)

    def test_list_own_lab_teams(self):
        """
        * Lab members can view their own teams
        """
        self.client.force_authenticate(self.user)
        result = self.client.get(reverse(f'team-list'))
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(result.json()), 1)
        team_ids = [t['id'] for t in result.json()]
        self.assertIn(self.lab_team.id, team_ids)

    def test_lab_admins_can_see_lab_teams(self):
        """
        * Lab admins can view their lab teams
        """
        self.client.force_authenticate(self.admin)
        result = self.client.get(reverse(f'team-list'))
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(result.json()), 2)
        team_ids = [t['id'] for t in result.json()]
        self.assertIn(self.lab_team.id, team_ids)
        self.assertIn(self.lab_other_team.id, team_ids)
        for t in team_ids:
            self.assertEqual(Team.objects.get(id=t).lab, self.lab, msg="Found team from another lab")

    def test_lab_admins_can_create_teams(self):
        """
        * Lab admins can create teams for their own lab
        """
        self.client.force_authenticate(self.admin)
        body = {'name': 'new_team', 'lab': self.lab.id}
        result = self.client.post(reverse(f'team-list'), body)
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_201_CREATED)
        j = result.json()
        self.assertEqual(j['name'], body['name'])
        self.assertEqual(len(j['member_group']['users']), 0)
        self.assertEqual(len(j['admin_group']['users']), 0)

    def test_lab_admins_cannot_create_teams_elsewhere(self):
        """
        * Lab admins can create teams for their own lab
        """
        self.client.force_authenticate(self.admin)
        body = {'name': 'new_team', 'lab': self.strange_lab.id}
        result = self.client.post(reverse(f'team-list'), body)
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lab_admins_can_add_and_remove_admins(self):
        """
        * Lab admins can add/remove users to/from their lab and its teams
        """
        self.client.force_authenticate(self.admin)
        body = {'add_users': [self.associate.id]}
        result = self.client.patch(reverse(f'{stub}-detail', args=(self.lab.admin_group.id,)), body)
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_200_OK)
        self.assertIn(self.associate.id, [u['id'] for u in result.json()['users']])

        body = {'remove_users': [self.associate.id]}
        result = self.client.patch(reverse(f'{stub}-detail', args=(self.lab.admin_group.id,)), body)
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.associate.id, [u['id'] for u in result.json()['users']])

    def test_lab_admins_cannot_add_admins_elsewhere(self):
        """
        * Lab admins can add/remove users to/from their lab and its teams
        """
        self.client.force_authenticate(self.admin)
        body = {'add_users': [self.associate.id]}
        result = self.client.patch(reverse(f'{stub}-detail', args=(self.strange_lab.admin_group.id,)), body)
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_403_FORBIDDEN)

    def test_lab_admins_cannot_remove_last_admin(self):
        """
        * Labs must have at least one admin
        """
        self.client.force_authenticate(self.admin)
        body = {'remove_users': [self.admin.id]}
        result = self.client.patch(reverse(f'{stub}-detail', args=(self.lab.admin_group.id,)), body)
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admins_can_add_and_remove_team_admins(self):
        """
        * Lab admins can add/remove users to/from their lab and its teams
        """
        self.client.force_authenticate(self.admin)
        body = {'add_users': [self.associate.id]}
        result = self.client.patch(reverse(f'{stub}-detail', args=(self.lab_team.admin_group.id,)), body)
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_200_OK)
        self.assertIn(self.associate.id, [u['id'] for u in result.json()['users']])

        # Now associate is admin, they should be able to add and remove admins
        self.client.force_authenticate(self.associate)
        body = {'add_users': [self.colleague.id]}
        result = self.client.patch(reverse(f'{stub}-detail', args=(self.lab_team.admin_group.id,)), body)
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_200_OK)
        self.assertIn(self.colleague.id, [u['id'] for u in result.json()['users']])

        # and members
        body = {'add_users': [self.user.id]}
        result = self.client.patch(reverse(f'{stub}-detail', args=(self.lab_team.member_group.id,)), body)
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_200_OK)
        self.assertIn(self.user.id, [u['id'] for u in result.json()['users']])

        # Members can't add or remove anyone
        self.client.force_authenticate(self.user)
        for approach in ['add_users', 'remove_users']:
            for group in [self.lab_team.admin_group, self.lab_team.member_group]:
                body = {approach: [self.colleague.id]}
                result = self.client.patch(reverse(f'{stub}-detail', args=(group.id,)), body)
                assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_403_FORBIDDEN)

        # Admins can remove members including themselves
        self.client.force_authenticate(self.associate)
        body = {'remove_users': [self.user.id, self.associate.id]}
        result = self.client.patch(reverse(f'{stub}-detail', args=(self.lab_team.member_group.id,)), body)
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.user.id, [u['id'] for u in result.json()['users']])
        self.assertNotIn(self.associate.id, [u['id'] for u in result.json()['users']])

        # No associate is longer admin, should error trying to remove colleague
        body = {'remove_users': [self.colleague.id]}
        result = self.client.patch(reverse(f'{stub}-detail', args=(self.lab.admin_group.id,)), body)
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_403_FORBIDDEN)

        # But the Lab admin can still remove them
        self.client.force_authenticate(self.admin)
        result = self.client.patch(reverse(f'{stub}-detail', args=(self.lab_team.admin_group.id,)), body)
        assert_response_property(self, result, self.assertEqual, result.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.colleague.id, [u['id'] for u in result.json()['users']])

if __name__ == '__main__':
    unittest.main()
