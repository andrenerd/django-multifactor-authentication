from django.db import models
from django.contrib.auth.hashers import check_password, is_password_usable, make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from django_otp.util import random_hex

from .abstract import AbstractDevice, AbstractUserMixin, PASSCODE_EXPIRY


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)


class UsernameDevice(AbstractDevice):
    username = models.CharField(max_length=150, unique=True)
    # reserved # hardcode = models.CharField(max_length=128) # experimental

    USER_MIXIN = 'UsernameUserMixin'
    IDENTIFIER_FIELD = 'username'

    def __eq__(self, other):
        if not isinstance(other, UsernameDevice):
            return False

        return self.username == other.username \
            and self.key == other.key

    def __hash__(self):
        return hash((self.username,))

    def is_interactive(self):
        return False

    def verify_is_allowed(self):
        return (False, None)


class UsernameUserMixin(AbstractUserMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(_('Username'), max_length=150, blank=True, null=True, unique=True, # editable=False
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )

    IDENTIFIER = 'username'

    class Meta:
        abstract = True

    def __str__(self):
        return str(getattr(self, 'username'))

    @property
    def is_username_confirmed(self):
        device = self.get_username_device()
        return device.confirmed if device else False

    def clean(self):
        super().clean()

        if self.username:
            self.username = self.__class__.objects.normalize_username(self.username)

    def get_username_device(self):
        username = getattr(self, 'username', '')

        try:
            device = UsernameDevice.objects.get(user=self, username=username)
        except UsernameDevice.DoesNotExist:
            device = None

        return device

    def verify_username(self, request=None):
        pass

    def verify(self, request=None):
        super().verify(request)
