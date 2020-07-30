from django.utils.translation import gettext_lazy as _

from rest_framework import authentication
from rest_framework import exceptions


class TokenQueryAuthentication(authentication.TokenAuthentication):
    """
    Let to pass token as query param (?token=QWERTY...)
    """
    def authenticate(self, request):
        token = request.GET.get('token', None)
        return self.authenticate_credentials(token) if token else \
            super(TokenQueryAuthentication, self).authenticate(request)


class TokenInactiveAuthentication(authentication.TokenAuthentication):
    """
    Let to authentication non active users by token
    Supposed to be used by specific endpoints only (signup, etc) 
    """
    def authenticate_credentials(self, key):
        model = self.get_model()

        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        return (token.user, token)
