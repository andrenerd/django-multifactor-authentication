from django.db import models
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .abstract import AbstractDevice, AbstractUserMixin


try:
    ChipProvider = settings.MULTAUTH_DEVICE_CHIP_PROVIDER
except AttributeError:
    from ..providers.bill import BillProvider
    ChipProvider = BillProvider


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)
MULTAUTH_TEMPLATE_NAME = getattr(settings, 'MULTAUTH_DEVICE_CHIP_TEMPLATE_NAME', 'chip')

TEMPLATE_MESSAGE_SUFFIX = '.txt'


class ChipDevice(AbstractDevice):
    """
    Something in your head
    https://www.youtube.com/watch?v=i92zJNGdW2U
    """
    chip = ChipNumberField(unique=True)
    hardcode = models.CharField(max_length=128) # experimental

    USER_MIXIN = 'ChipUserMixin'
    IDENTIFIER_FIELD = 'chip'

    def __eq__(self, other):
        if not isinstance(other, ChipDevice):
            return False

        return self.chip == other.chip \
            and self.key == other.key

    def __hash__(self):
        return hash((self.chip,))

    def generate_challenge(self, request=None):
        self.generate_token()

        if MULTAUTH_DEBUG:
            print('Fake auth message, chip: %s, token: %s ' % (self.email, self.token))

        else:
            context = {
                'token': self.token,
            }

            pass


# TODO: add mixin
