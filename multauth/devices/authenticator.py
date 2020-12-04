from django.db import models
from django.utils.module_loading import import_string
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from django_otp.util import random_hex

from .abstract import AbstractDevice, AbstractUserMixin


try:
    AuthenticatorProviderPath = settings.MULTAUTH_DEVICE_AUTHENTICATOR_PROVIDER
    AuthenticatorProvider = import_string(AuthenticatorProviderPath) # ex. multauth.providers.GauthenticatorProvider
except AttributeError:
    from ..providers.mail import GauthenticatorProvider
    AuthenticatorProvider = GauthenticatorProvider


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)


class AuthenticatorDevice(AbstractDevice):
    USER_MIXIN = 'AuthenticatorUserMixin'

    def __eq__(self, other):
        if not isinstance(other, AuthenticatorDevice):
            return False

        return self.authenticator == other.authenticator \
            and self.key == other.key

    def __hash__(self):
        return hash((self.authenticator,))

    def clean(self):
        super().clean()

    def generate_challenge(self, request=None):
        self.generate_token()

        if MULTAUTH_DEBUG:
            print('Fake auth code, Google Authenticator: %s, token: %s ' % (self.authenticator, self.token))

        return self.token


class AuthenticatorUserMixin(AbstractUserMixin):
    class Meta:
        abstract = True

    def __str__(self):
        return str(getattr(self, 'authenticator', ''))

    @property
    def is_authenticator_confirmed(self):
        return True

    def get_authenticator_device(self):
        return None

    def verify(self, request=None):
        super().verify(request)
