import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from galvanalyser.models import KnoxAuthToken
from .factories import UserFactory

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class TokenTests(APITestCase):
    def setUp(self):
        self.user = UserFactory.create(username='test_user')
        self.other_user = UserFactory.create(username='test_user_other')

    def test_crud(self):
        self.client.force_login(self.user)
        body = {'name': 'Test API token', 'ttl': 600}
        url = reverse('knox_create_token')
        print("Test create API token")
        response = self.client.post(url, body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('name'), body['name'])
        self.assertIn(response.json(), 'token')
        print("OK")

        print("Test list tokens")
        url = reverse('tokens-list')
        response = self.client.get(url)
        self.assertEqual(len(response.json()), 1)
        detail_url = response.json()['url']
        self.client.force_login(self.other_user)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
        print("OK")

        print("Test token detail")
        self.client.force_login(self.user)
        response = self.client.get(detail_url)
        self.assertEqual(response.json()['name'], body['name'])
        self.assertNotIn(response.json(), 'token')
        print("OK")

        print("Test update")
        new_name = "new token name"
        response = self.client.patch(detail_url, {"name": new_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], new_name)
        print("OK")

        print("Test token delete")
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(KnoxAuthToken.objects.filter(knox_token_key__regex=f"_{self.user.id}$").exists(), False)
        print("OK")


if __name__ == '__main__':
    unittest.main()
