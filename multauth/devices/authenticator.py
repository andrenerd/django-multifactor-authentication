from django.db import models
from django.utils.module_loading import import_string
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from django_otp.util import random_hex
from django_otp.plugins.otp_totp.models import TOTPDevice

from .abstract import AbstractDevice, AbstractUserMixin


# reserved 
# try:
#     AuthenticatorProviderPath = settings.MULTAUTH_DEVICE_AUTHENTICATOR_PROVIDER
#     AuthenticatorProvider = import_string(AuthenticatorProviderPath) # ex. multauth.providers.GauthenticatorProvider
# except AttributeError:
#     from ..providers.mail import GauthenticatorProvider
#     AuthenticatorProvider = GauthenticatorProvider


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)


class AuthenticatorDevice(AbstractDevice, TOTPDevice):
    token = None
    valid_until = None

    USER_MIXIN = 'AuthenticatorUserMixin'

    def __eq__(self, other):
        if not isinstance(other, AuthenticatorDevice):
            return False

        return self.key == other.key

    def __hash__(self):
        return hash((self.authenticator,))

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    # def generate_key(self):
    #     return 'AAAABBBBCCCCDDDD'

    def generate_token(self):
        return None

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
        try:
            device = AuthenticatorDevice.objects.get(user=self)
        except AuthenticatorDevice.DoesNotExist:
            device = None

        return device

    def verify(self, request=None):
        super().verify(request)
