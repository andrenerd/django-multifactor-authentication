from django.db import models
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .abstract import AbstractDevice


try:
    ChipProvider = settings.MULTAUTH_DEVICE_CHIP_PROVIDER
except AttributeError:
    from ..providers.bill import BillProvider
    ChipProvider = BillProvider


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)
MULTAUTH_TEMPLATE_NAME = getattr(settings, 'MULTAUTH_DEVICE_CHIP_TEMPLATE_NAME', 'phone')

TEMPLATE_MESSAGE_SUFFIX = '.txt'


class ChipDevice(AbstractDevice):
    """
    Model with microchip number and token seed linked to a user.
    """
    phone = ChipNumberField()
    pushcode = models.CharField(_('Pushcode'), max_length=256, blank=True, null=True, unique=True, editable=False)

    def __eq__(self, other):
        if not isinstance(other, ChipDevice):
            return False

        return self.phone == other.phone \
            and self.key == other.key

    def __hash__(self):
        return hash((self.phone,))

    def generate_challenge(self, request=None):
        token = self.get_token()

        if MULTAUTH_DEBUG:
            print('Fake auth message, chip: %s, token: %s ' % (self.email, token))

        else:
            context = {
                'token': token,
            }

            pass
