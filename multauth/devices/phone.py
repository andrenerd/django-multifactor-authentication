from django.db import models
from django.contrib.auth.hashers import check_password, is_password_usable, make_password
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from phonenumber_field.modelfields import PhoneNumberField
from django_otp.util import random_hex

from .abstract import AbstractDevice, AbstractUserMixin


try:
    PhoneProvider = settings.MULTAUTH_DEVICE_PHONE_PROVIDER
except AttributeError:
    from ..providers.twilio import TwilioProvider
    PhoneProvider = TwilioProvider


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)
MULTAUTH_CONFIRMED = getattr(settings, 'MULTAUTH_DEVICE_PHONE_CONFIRMED', True)
MULTAUTH_TEMPLATE_NAME = getattr(settings, 'MULTAUTH_DEVICE_PHONE_TEMPLATE_NAME', 'phone')

TEMPLATE_MESSAGE_SUFFIX = '.txt'


class PhoneDevice(AbstractDevice):
    """
    Could be also called as SmsDevice
    """
    phone = PhoneNumberField(unique=True)
    confirmed = models.BooleanField(default=MULTAUTH_CONFIRMED) # override parent
    hardcode = models.CharField(max_length=128) # experimental
    # TODO: make it optional or ?
    pushcode = models.CharField(max_length=256, blank=True, null=True, unique=True, editable=False)

    USER_MIXIN = 'PhoneUserMixin'
    IDENTIFIER_FIELD = 'phone'

    def __eq__(self, other):
        if not isinstance(other, PhoneDevice):
            return False

        return self.phone == other.phone \
            and self.key == other.key

    def __hash__(self):
        return hash((self.phone,))

    def clean(self):
        super().clean()

    def generate_challenge(self, request=None):
        self.generate_token()

        if MULTAUTH_DEBUG:
            print('Fake auth message, phone: %s, token: %s ' % (self.phone, self.token))

        else:
            context = {
                'token': self.token,
            }

            message = self._render_message(context)

            if message:
                PhoneProvider(
                    to=self.phone.as_e164,
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


class PhoneUserMixin(AbstractUserMixin):

    phone = PhoneNumberField(_('Phone number'), blank=True, null=True, unique=True,
        # help_text = _('Required.'),
        error_messages = {
            'unique': _('A user with that phone number already exists.'),
        }
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(getattr(self, 'phone', ''))

    @property
    def is_phone_confirmed(self):
        device = self.get_phone_device()
        return device.confirmed if device else False

    def get_phone_device(self):
        phone = getattr(self, 'phone', None)

        try:
            device = PhoneDevice.objects.get(user=self, phone=phone)
        except PhoneDevice.DoesNotExist:
            device = None

        return device

    def verify_phone(self, request=None):
        if getattr(self, 'phone', None):
            device = self.get_phone_device()

            if not device:
                device = PhoneDevice(
                    user=self,
                    name='default', # temporal
                    phone=self.phone,
                    key=random_hex(20), # OBSOLETED: .decode('ascii'),
                    confirmed=False,
                )

                device.save()

            device.generate_challenge(request)
            return device

    def verify_phone_token(self, token):
        if getattr(self, 'phone', None):
            device = self.get_phone_device()

            if not device:
                return False

            return device.verify_token(token) if token else False

    def verify(self, request=None):
        super().verify(request)

        if self.phone and not self.is_phone_confirmed:
            self.verify_phone(request)
