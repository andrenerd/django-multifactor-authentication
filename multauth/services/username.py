from django.db import models
from django.contrib.auth.hashers import check_password, is_password_usable, make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from django_otp.util import random_hex

from .abstract import AbstractService, AbstractUserMixin, PASSCODE_EXPIRY


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)


class UsernameService(AbstractService):
    USER_MIXIN = 'UsernameUserMixin'
    IDENTIFIER_FIELD = 'username'

    class Meta:
        abstract = True


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

    def clean(self):
        super().clean()

        if self.username:
            self.username = self.__class__.objects.normalize_username(self.username)

    def get_username_service(self):
        return None # todo: or UsernameService()?

    def verify(self, request=None):
        super().verify(request)
