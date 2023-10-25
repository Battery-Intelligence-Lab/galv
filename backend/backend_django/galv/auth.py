from rest_framework import exceptions, HTTP_HEADER_ENCODING
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from django.utils.translation import gettext_lazy as _

from .models import Harvester, HarvesterUser


class HarvesterAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Harvester ".  For example:

        Authorization: Harvester 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'Harvester'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode(encoding=HTTP_HEADER_ENCODING):
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode(encoding=HTTP_HEADER_ENCODING)
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            harvester = Harvester.objects.get(api_key=key)
        except Harvester.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        user = HarvesterUser(harvester)
        if not user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (user, key)

    def authenticate_header(self, request):
        return self.keyword