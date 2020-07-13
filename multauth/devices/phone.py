from django.db import models
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from phonenumber_field.modelfields import PhoneNumberField

from .abstract import AbstractDevice


try:
    PhoneProvider = settings.MULTAUTH_DEVICE_PHONE_PROVIDER
except AttributeError:
    from ..providers.twilio import TwilioProvider
    PhoneProvider = TwilioProvider


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)
MULTAUTH_TEMPLATE_NAME = getattr(settings, 'MULTAUTH_DEVICE_PHONE_TEMPLATE_NAME', 'phone')

TEMPLATE_MESSAGE_SUFFIX = '.txt'


class PhoneDevice(AbstractDevice):
    """
    Model with phone number and token seed linked to a user.
    """
    phone = PhoneNumberField()
    pushcode = models.CharField(_('Pushcode'), max_length=256, blank=True, null=True, unique=True, editable=False)

    USER_MIXIN = 'devices.PhoneUserMixin'

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
            print('Fake auth message, phone: %s, token: %s ' % (self.phone, token))

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


class PhoneUserMixin():

    phone = PhoneNumberField(_('Phone number'), blank=True, null=True, unique=True,
        #help_text = _('Required.'),
        error_messages = {
            'unique': _('A user with that phone number already exists.'),
        }
    )

    passcode = models.CharField(_('Passcode'), max_length=128) # editable=False

    is_phone_verified = models.BooleanField(_('Phone verified'), default=False,
        help_text=_('Designates whether this user phone is verified.'),
    )

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
        """ Symlink """
        if self.phone and not self.is_phone_verified:
            self.verify_phone(request)

    def set_passcode(self, raw_passcode):
        self.passcode = make_password(raw_passcode)
        self._passcode = raw_passcode

    def check_passcode(self, raw_passcode):
        """
        Return a boolean of whether the raw_passcode was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_passcode):
            self.set_passcode(raw_passcode)

            # Password hash upgrades shouldn't be considered passcode changes.
            self._passcode = None
            self.save(update_fields=['passcode'])

        return check_password(raw_passcode, self.passcode, setter)

    def set_unusable_passcode(self):
        # Set a value that will never be a valid hash
        self.passcode = make_password(None)

    def has_usable_passcode(self):
        """
        Return False if set_unusable_passcode() has been called for this user.
        """
        return is_passcode_usable(self.passcode)
