# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import base64

from django.urls import reverse
from rest_framework.test import APITestCase


def assert_response_property(self, response, assertion, *args, **kwargs):
    try:
        assertion(*args, **kwargs)
    except AssertionError as e:
        raise AssertionError(f"{e}\nResponse: {response.json()}")


class GalvTestCase(APITestCase):

    def get_token_header_for_user(self, user):
        self.client.force_login(user)
        user.set_password('foobar')
        user.save()
        auth_str = base64.b64encode(bytes(f"{user.username}:foobar", 'utf-8'))
        basic_auth = self.client.post(
            reverse('knox_login'),
            {},
            HTTP_AUTHORIZATION=f"Basic {auth_str.decode('utf-8')}"
        )
        token = basic_auth.json()['token']
        return {'HTTP_AUTHORIZATION': f"Bearer {token}"}

