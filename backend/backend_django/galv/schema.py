# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from knox.settings import knox_settings

class KnoxTokenScheme(OpenApiAuthenticationExtension):
    target_class = 'knox.auth.TokenAuthentication'
    name = 'knoxTokenAuth'
    match_subclasses = True
    priority = 1

    def get_security_definition(self, auto_schema):
        if knox_settings.AUTH_HEADER_PREFIX == 'Bearer':
            return {
                'type': 'http',
                'scheme': 'bearer',
            }
        else:
            return {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Token-based authentication with required prefix "%s"' % knox_settings.AUTH_HEADER_PREFIX
            }

class HarvesterAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'galv.auth.HarvesterAuthentication'
    name = 'harvesterAuth'
    match_subclasses = True
    priority = 1

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Harvester API key'
        }

def custom_preprocessing_hook(endpoints):
    # your modifications to the list of operations that are exposed in the schema
    for (path, path_regex, method, callback) in endpoints:
        pass
    return endpoints

def custom_postprocessing_hook(result, generator, request, public):
    # your modifications to the schema in parameter result
    return result