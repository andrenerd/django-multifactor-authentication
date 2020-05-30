from django.db import models
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from phonenumber_field.modelfields import PhoneNumberField

from .abstract import AbstractDevice
from ..providers import TwilioProvider


PhoneProvider = getattr(settings, 'MULTAUTH_PHONE_PROVIDER', TwilioProvider)


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)
MULTAUTH_TEMPLATE_NAME = getattr(settings, 'MULTAUTH_PHONE_TEMPLATE_NAME', 'phone')

TEMPLATE_MESSAGE_SUFFIX = '.txt'


class PhoneDevice(AbstractDevice):
    """
    Model with phone number and token seed linked to a user.
    """
    phone = PhoneNumberField()
    pushcode = models.CharField(_('Pushcode'), max_length=256, blank=True, null=True, unique=True, editable=False)

    def __eq__(self, other):
        if not isinstance(other, PhoneDevice):
            return False

        return self.phone == other.phone \
            and self.key == other.key

    def __hash__(self):
        return hash((self.phone,))

    def generate_challenge(self, request=None):
        token = self.get_token()

        if MULTAUTH_DEBUG:
            print('Fake auth message, phone: %s, token: %s ' % (self.email, token))

        else:
            context = {
                'token': token,
            }

            message = _render_message(context)

            if message:
                PhoneProvider(
                    to=self.phone.as_e164,
                    message=message,
                ).send()

    def _render_message(self, context):
        if hasattr(self, '_template_message'):
            return self._render_template(self._template_message, context)

        else:
            try:
                TEMPLATE_MESSAGE = get_template('multauth/' + MULTAUTH_TEMPLATE_NAME + TEMPLATE_MESSAGE_SUFFIX)
            except (TemplateDoesNotExist, TemplateSyntaxError):
                if DEBUG: raise TemplateDoesNotExist('Template: {}'.format(MULTAUTH_TEMPLATE_NAME))
                TEMPLATE_MESSAGE = None

            self._template_message = TEMPLATE_MESSAGE
            return self._render_template(self._template_message, context)

    def  _render_template(self, template, context):
        if template:
            return _(template.render(context)).strip()
        else:
            return None
