# based on django-otp-yubikey

# import time
from base64 import b64decode
from binascii import hexlify, unhexlify

from django.db import models
# from django.utils.module_loading import import_string
# from django.template.loader import get_template
# from django.template import TemplateDoesNotExist, TemplateSyntaxError
# from django.utils.translation import gettext_lazy as _
# from django.conf import settings

# from django_otp.models import ThrottlingMixin
# from django_otp.util import hex_validator, random_hex
# from django_otp.oath import TOTP

# from yubiotp.client import YubiClient10, YubiClient11, YubiClient20
from yubiotp.modhex import modhex
from yubiotp.otp import decode_otp

from .abstract import AbstractService, PasscodeServiceMixin, AbstractUserMixin


# reserved
# try:
#     YubikeyProviderPath = settings.MULTAUTH_SERVICE_YUBIKEY_PROVIDER
#     YubikeyProvider = import_string(YubikeyProviderPath) # ex. multauth.providers.GyubikeyProvider
# except AttributeError:
#     from ..providers.mail import GyubikeyProvider
#     YubikeyProvider = GyubikeyProvider


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)
MULTAUTH_PRIVATE_ID_LENGTH = getattr(settings, 'MULTAUTH_SERVICE_YUBIKEY_PRIVATE_ID_LENGTH', 6)
# MULTAUTH_SYNC = getattr(settings, 'MULTAUTH_SERVICE_YUBIKEY_SYNC', True)
# MULTAUTH_THROTTLE_FACTOR = getattr(settings, 'MULTAUTH_SERVICE_YUBIKEY_THROTTLE_FACTOR', 1)
# MULTAUTH_ISSUER = getattr(settings, 'MULTAUTH_SERVICE_YUBIKEY_ISSUER', 'Multauth')


# # see django_otp.plugins.otp_totp.models.TOTPService
# def key_generator():
#     return random_hex(MULTAUTH_KEY_LENGTH)


# # see django_otp.plugins.otp_totp.models.TOTPService
# def key_validator(value):
#     return hex_validator()(value)


def private_id_generator():
    return force_text(random_hex(MULTAUTH_PRIVATE_ID_LENGTH))


def private_id_validator(value):
    return hex_validator(MULTAUTH_PRIVATE_ID_LENGTH)(value)


def key_generator():
    return force_text(random_hex(MULTAUTH_PRIVATE_ID_LENGTH))


def key_validator(value):
    return hex_validator(MULTAUTH_PRIVATE_ID_LENGTH)(value)


class YubikeyService(PasscodeServiceMixin, AbstractService):
    private_id = models.CharField(max_length=MULTAUTH_PRIVATE_ID_LENGTH * 2, validators=[private_id_validator], default=private_id_generator)
    key = models.CharField(max_length=32, validators=[key_validator], default=key_generator)
    session = models.PositiveIntegerField(default=0)
    counter = models.PositiveIntegerField(default=0)

    USER_MIXIN = 'YubikeyUserMixin'

    # def __eq__(self, other):
    #     if not isinstance(other, YubikeyService):
    #         return False

    #     return self.key == other.key

    # useless?
    # def __hash__(self):
    #     return hash((self.key,))

    def is_interactive(self):
        return False

    # # see django_otp.plugins.otp_totp.models.TOTPService
    @property
    def bin_key(self):
        return unhexlify(self.key.encode())

    # @property
    # def key_b32(self):
    #     return b32encode(self.bin_key)

    # # see django_otp.plugins.otp_totp.models.TOTPService
    # @property
    # def key_uri(self):
    #     user = self.user
    #     label = quote([str(getattr(user, i)) for i in user.IDENTIFIERS if getattr(user, i)].pop())
    #     issuer = quote(str(MULTAUTH_ISSUER).replace(':', ''))

    #     params = {
    #         'secret': self.key_b32, # should go first
    #         # 'algorithm': 'SHA1',
    #         'digits': self.digits,
    #         'period': self.step,
    #     }
    #     urlencoded_params = urlencode(params)

    #     if issuer:
    #         label = '{}:{}'.format(issuer, label)
    #         urlencoded_params += '&issuer={}'.format(quote(issuer))  # encode issuer as per RFC 3986, not quote_plus

    #     url = 'otpauth://totp/{}?{}'.format(label, urlencoded_params)
    #     return url

    def public_id(self):
        return modhex(pack('>I', self.id))

    # def clean(self):
    #     super().clean()

    # def save(self, *args, **kwargs):
    #     if not self.key:
    #         self.key = self.generate_key()
    #     return super().save(*args, **kwargs)

    # def set_key(self, raw_hardcode):
    #     self.key = key_generator()
    #     self.save(update_fields=['key'])
    #     return self.key

    # def generate_totp(self, request=None):
    #     key = self.bin_key
    #     totp = TOTP(key, self.step, self.t0, self.digits, self.drift)
    #     totp.time = time.time()
    #     return totp

    # def generate_challenge(self, request=None):
    #     totp = self.generate_totp()

    #     if MULTAUTH_DEBUG:
    #         print('Fake auth message, Yubikey, token: %s ' % (totp.token()))

    # see django_otp.plugins.otp_totp.models.TOTPService
    def verify_token(self, token):
        verify_allowed, _ = self.verify_is_allowed()
        if not verify_allowed:
            return False

        if isinstance(token, str):
            token = token.encode('utf-8')

        try:
            public_id, otp = decode_otp(token, self.bin_key)
        except Exception:
            return False

        if public_id != self.public_id():
            return False

        if hexify(otp.uid) != self.private_id.encode():
            return False

        if otp.session < self.session:
            return False

        if (otp.session == self.session) and (otp.counter <= self.counter):
            return False

        self.session = otp.session
        self.counter = otp.counter
        self.save()

        return True


class YubikeyValidationService(models.Model):
    pass


class YubikeyUserMixin(AbstractUserMixin):
    class Meta:
        abstract = True

    # def __str__(self):
    #     return str(getattr(self, 'yubikey', ''))

    # def check_yubikey_passcode(self, passcode):
    #     service = self.get_yubikey_service()

    #     if not service:
    #         return False

    #     return service.check_passcode(passcode) if passcode else False

    def get_yubikey_service(self):
        try:
            service = YubikeyService.objects.get(user=self)
        except YubikeyService.DoesNotExist:
            service = None

        return service

    # def verify(self, request=None):
    #     super().verify(request)
