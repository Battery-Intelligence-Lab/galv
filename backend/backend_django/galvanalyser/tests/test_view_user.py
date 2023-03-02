import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging
import base64

from .factories import UserFactory
from galvanalyser.models import VouchFor
from django.contrib.auth.models import User

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class UserTests(APITestCase):
    def setUp(self):
        self.non_user = UserFactory.create(username='test_users', is_active=True)
        self.non_user_inactive = UserFactory.create(username='test_users_inactive')
        self.non_user_inactive.is_active = False
        self.non_user_inactive.save()
        self.user = UserFactory.create(username='test_users_user', is_active=True)
        self.client.force_login(self.user)
        self.user.set_password('foobar')
        self.user.save()
        auth_str = base64.b64encode(bytes(f"{self.user.username}:foobar", 'utf-8'))
        basic_auth = self.client.post(
            reverse('knox_login'),
            {},
            HTTP_AUTHORIZATION=f"Basic {auth_str.decode('utf-8')}"
        )
        token = basic_auth.json()['token']
        self.headers = {'HTTP_AUTHORIZATION': f"Bearer {token}"}

    def test_create(self):
        url = reverse('inactive_user-list')
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], data['username'])
        self.assertEqual(response.json()['is_active'], False)
        print("OK")

    def test_activate(self):
        self.client.force_login(self.user)
        print("Test Inactive User list")
        url = reverse('inactive_user-list')
        response = self.client.get(url, **self.headers)
        json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]['username'], self.non_user_inactive.username)
        print("OK")
        print("Test Inactive User activate")
        url = reverse('inactive_user-vouch-for', args=(self.non_user_inactive.id,))
        response = self.client.get(url, **self.headers)
        json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['username'], self.non_user_inactive.username)
        self.assertEqual(User.objects.get(id=self.non_user_inactive.id).is_active, True)
        self.assertTrue(VouchFor.objects.filter(new_user=self.non_user_inactive, vouching_user=self.user).exists())
        print("OK")

    def test_update(self):
        url = reverse('user-detail', args=(self.user.id,))
        print("Test update rejected (no current password)")
        self.client.force_login(self.user)
        body = {'email': 'test.user@example.com', 'password': 'complex_password'}
        self.assertEqual(
            self.client.patch(url, body, **self.headers).status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        print("OK")
        print("Test update rejected (no access to others)")
        body['currentPassword'] = 'password'
        self.user.set_password(body['currentPassword'])
        self.user.save()
        self.assertEqual(
            self.client.patch(reverse('user-detail', args=(self.non_user.id,)), body, **self.headers).status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        print("OK")
        print("Test update rejected (invalid email)")
        self.assertEqual(
            self.client.patch(url, {**body, 'email': 'bad-email'}, **self.headers).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        print("OK")
        print("Test update okay")
        response = self.client.patch(url, body, **self.headers)
        json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json['email'], body['email'])
        self.assertTrue(User.objects.get(id=self.user.id).check_password(body['password']))
        print("OK")


if __name__ == '__main__':
    unittest.main()
