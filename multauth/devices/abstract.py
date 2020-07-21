from binascii import unhexlify
from django.db import models
from django.conf import settings

from django_otp.oath import totp
from django_otp.util import hex_validator, random_hex
from django_otp.models import Device


TOKEN_LENGTH = getattr(settings, 'MULTAUTH_TOKEN_LENGTH', 6) # 6 digits
TOKEN_EXPIRY = getattr(settings, 'MULTAUTH_TOKEN_EXPIRY', 3600 * 24 * 3) # 3 days


def key_validator(*args, **kwargs):
    """
    Just a wrapper
    """
    return hex_validator()(*args, **kwargs)


class AbstractDevice(Device):

    key = models.CharField(
        max_length=40,
        validators=[key_validator],
        default=random_hex,
        help_text='Hex-encoded secret key'
    )

    class Meta:
        app_label = 'multauth'
        abstract = True

    def __str__(self):
      raise NotImplementedError

    @property
    def bin_key(self):
        return unhexlify(self.key.encode())

    def get_token(self):
        return str(totp(self.bin_key, digits=TOKEN_LENGTH)).zfill(TOKEN_LENGTH)

    def verify_token(self, token):
        try:
            token = int(token)
        except ValueError:
            return False

        for drift in range(-5, 1):
            if totp(self.bin_key, drift=drift, digits=TOKEN_LENGTH) == token:
                return True

        return False

    def generate_challenge(self, request=None):
      raise NotImplementedError


class AbstractUserMixin(models.Model):

    IDENTIFIER_FIELD = None # required
    SECRET_FIELD = None # semi-required

    class Meta:
        abstract = True

    def clean(self):
        pass

    def verify(self, request=None):
        pass

    def set_secrets(self, **fields):
        pass

    def check_secrets(self, **fields):
        pass
