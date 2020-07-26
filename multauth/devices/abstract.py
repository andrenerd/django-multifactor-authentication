from binascii import unhexlify
from django.db import models
from django.contrib.auth.hashers import check_password, make_password
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
    """
    Device token, one-time password, is used under "name" passcode.
    To not mess it with authorization token.
    (term "token" is derived from device_otp package and kept for Devices)
    """
    key = models.CharField(
        max_length=40,
        validators=[key_validator],
        default=random_hex,
        help_text='Hex-encoded secret key'
    )

    USER_MIXIN = None # required
    IDENTIFIER_FIELD = None # required

    # see _password attribure in AbstractBaseUser
    _hardcode = None

    class Meta:
        app_label = 'multauth'
        abstract = True

    # def __str__(self):
    #   raise NotImplementedError

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

    @property
    def has_hardcode(self):
        return hastattr(self, 'hardcode')

    # based on check_hardcode from django.contrib.auth.hashers
    def set_hardcode(self, raw_hardcode):
        if not self.has_hardcode:
            raise self.__class__.FieldDoesNotExist('Hardcode not supported by the device')

        self.hardcode = make_password(raw_hardcode)
        # reserved # self._hardcode = raw_hardcode

    # based on check_hardcode from django.contrib.auth.hashers
    def check_hardcode(self, raw_hardcode):
        if not self.has_hardcode:
            raise self.__class__.FieldDoesNotExist('Hardcode not supported by the device')

        def setter(raw_hardcode):
            self.set_hardcode(raw_hardcode)
            self._hardcode = None
            self.save(update_fields=['hardcode'])

        return check_password(raw_hardcode, self.hardcode, setter)


class AbstractUserMixin(models.Model):

    class Meta:
        abstract = True

    def clean(self):
        pass

    def verify(self, request=None):
        pass

