from binascii import unhexlify
from django.db import models
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings

from django_otp.oath import totp
from django_otp.util import hex_validator, random_hex
from django_otp.models import Device, SideChannelDevice


PASSCODE_LENGTH = getattr(settings, 'MULTAUTH_PASSCODE_LENGTH', 6) # n digits
PASSCODE_EXPIRY = getattr(settings, 'MULTAUTH_PASSCODE_EXPIRY', 3600) # n secs


class AbstractService(models.Model):
    USER_MIXIN = None # required
    IDENTIFIER_FIELD = None # required

    class Meta:
        app_label = 'multauth'
        abstract = True

    # def __str__(self):
    #   raise NotImplementedError


class PasscodeServiceMixin(SideChannelDevice):
    class Meta:
        app_label = 'multauth'
        abstract = True

    def generate_token(self, length=PASSCODE_LENGTH, valid_secs=PASSCODE_EXPIRY):
        """
        django_otp:
        Service token, or one-time password, is used under name "passcode".
        To not mess it with authorization token.
        (term "token" is derived from device_otp package and kept for Services)
        """
        super().generate_token(length, valid_secs)

    # obsoleted
    # @property
    # def has_passcode(self):
    #     return True

    def check_passcode(self, raw_passcode):
        return bool(self.verify_token(raw_passcode))


class HardcodeServiceMixin():
    _hardcode = None # see _password attribure in AbstractBaseUser

    class Meta:
        app_label = 'multauth'
        abstract = True

    # obsoleted
    # @property
    # def has_hardcode(self):
    #     return True

    # based on check_hardcode from django.contrib.auth.hashers
    def set_hardcode(self, raw_hardcode):
        self.hardcode = make_password(raw_hardcode)
        # reserved # self._hardcode = raw_hardcode

    # based on check_hardcode from django.contrib.auth.hashers
    def check_hardcode(self, raw_hardcode):
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

