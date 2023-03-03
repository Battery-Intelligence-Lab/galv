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
