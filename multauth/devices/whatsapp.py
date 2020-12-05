from django.db import models
from django.utils.module_loading import import_string
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from phonenumber_field.modelfields import PhoneNumberField
from django_otp.util import random_hex

from .abstract import AbstractSideChannelDevice, AbstractUserMixin


try:
    WhatsappProviderPath = settings.MULTAUTH_DEVICE_WHATSAPP_PROVIDER
    WhatsappProvider = import_string(WhatsappProviderPath) # ex. multauth.providers.VonageProvider
except AttributeError:
    from ..providers.twilio import TwilioProvider
    WhatsappProvider = TwilioProvider


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)
MULTAUTH_CONFIRMED = getattr(settings, 'MULTAUTH_DEVICE_WHATSAPP_CONFIRMED', True)
MULTAUTH_TEMPLATE_NAME = getattr(settings, 'MULTAUTH_DEVICE_WHATSAPP_TEMPLATE_NAME', 'whatsapp')

TEMPLATE_MESSAGE_SUFFIX = '.txt'


class WhatsappDevice(AbstractSideChannelDevice):
    whatsapp = PhoneNumberField(unique=True)
    confirmed = models.BooleanField(default=MULTAUTH_CONFIRMED) # override parent
    # TODO: make it optional or ?
    pushcode = models.CharField(max_length=256, blank=True, null=True, unique=True, editable=False)

    USER_MIXIN = 'WhatsappUserMixin'
    IDENTIFIER_FIELD = 'whatsapp'

    def __eq__(self, other):
        if not isinstance(other, WhatsappDevice):
            return False

        return self.whatsapp == other.whatsapp \
            and self.key == other.key

    def __hash__(self):
        return hash((self.whatsapp,))

    def clean(self):
        super().clean()

    def generate_challenge(self, request=None):
        self.generate_token()

        if MULTAUTH_DEBUG:
            print('Fake auth message, whatsapp: %s, token: %s ' % (self.whatsapp, self.token))

        else:
            context = {
                'token': self.token,
            }

            message = self._render_message(context)

            if message:
                WhatsappProvider(
                    to='whatsapp:' + self.whatsapp.as_e164,
                    message=message,
                ).send()

        return self.token

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


class WhatsappUserMixin(AbstractUserMixin):

    whatsapp = PhoneNumberField(_('WhatsApp identifier'), blank=True, null=True, unique=True,
        # help_text = _('Required.'),
        error_messages = {
            'unique': _('A user with that WhatsApp identifier already exists.'),
        }
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(getattr(self, 'whatsapp', ''))

    @property
    def is_whatsapp_confirmed(self):
        device = self.get_whatsapp_device()
        return device.confirmed if device else False

    def get_whatsapp_device(self):
        whatsapp = getattr(self, 'whatsapp', None)

        try:
            device = WhatsappDevice.objects.get(user=self, whatsapp=whatsapp)
        except WhatsappDevice.DoesNotExist:
            device = None

        return device

    def verify_whatsapp(self, request=None):
        if getattr(self, 'whatsapp', None):
            device = self.get_whatsapp_device()

            if not device:
                device = WhatsappDevice(
                    user=self,
                    name='default', # temporal
                    whatsapp=self.whatsapp,
                    key=random_hex(20), # OBSOLETED: .decode('ascii'),
                    confirmed=False,
                )

                device.save()

            device.generate_challenge(request)
            return device

    def verify_whatsapp_token(self, token):
        if getattr(self, 'whatsapp', None):
            device = self.get_whatsapp_device()

            if not device:
                return False

            return device.verify_token(token) if token else False

    def verify(self, request=None):
        super().verify(request)

        if self.whatsapp and not self.is_whatsapp_confirmed:
            self.verify_whatsapp(request)
