from binascii import unhexlify
from django.db import models
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings

from django_otp.oath import totp
from django_otp.util import hex_validator, random_hex
from django_otp.models import SideChannelDevice


PASSCODE_LENGTH = getattr(settings, 'MULTAUTH_PASSCODE_LENGTH', 6) # n digits
PASSCODE_EXPIRY = getattr(settings, 'MULTAUTH_PASSCODE_EXPIRY', 3600) # n secs


class AbstractDevice(SideChannelDevice):
    USER_MIXIN = None # required
    IDENTIFIER_FIELD = None # required

    # see _password attribure in AbstractBaseUser
    _hardcode = None

    class Meta:
        app_label = 'multauth'
        abstract = True

    # def __str__(self):
    #   raise NotImplementedError

    def generate_token(self, length=PASSCODE_LENGTH, valid_secs=PASSCODE_EXPIRY):
        """
        Device token, or one-time password, is used under name "passcode".
        To not mess it with authorization token.
        (term "token" is derived from device_otp package and kept for Devices)
        """
        super().generate_token(length, valid_secs)

    @property
    def has_hardcode(self):
        return hasattr(self, 'hardcode')

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

