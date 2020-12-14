from django.db import models
from django.utils.module_loading import import_string
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from phonenumber_field.modelfields import PhoneNumberField
from django_otp.util import random_hex

from .abstract import AbstractService, PasscodeServiceMixin, AbstractUserMixin


try:
    WhatsappProviderPath = settings.MULTAUTH_SERVICE_WHATSAPP_PROVIDER
    WhatsappProvider = import_string(WhatsappProviderPath) # ex. multauth.providers.VonageProvider
except AttributeError:
    from ..providers.twilio import TwilioProvider
    WhatsappProvider = TwilioProvider


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)
MULTAUTH_CONFIRMED = getattr(settings, 'MULTAUTH_SERVICE_WHATSAPP_CONFIRMED', True)
MULTAUTH_TEMPLATE_NAME = getattr(settings, 'MULTAUTH_SERVICE_WHATSAPP_TEMPLATE_NAME', 'whatsapp')

TEMPLATE_MESSAGE_SUFFIX = '.txt'


class WhatsappService(PasscodeServiceMixin, AbstractService):
    whatsapp = PhoneNumberField(unique=True)
    confirmed = models.BooleanField(default=MULTAUTH_CONFIRMED) # override parent

    USER_MIXIN = 'WhatsappUserMixin'
    IDENTIFIER_FIELD = 'whatsapp'

    def __eq__(self, other):
        if not isinstance(other, WhatsappService):
            return False

        return self.whatsapp == other.whatsapp \
            and self.key == other.key

    def __hash__(self):
        return hash((self.whatsapp,))

    def clean(self):
        super().clean()

    def set_passcode(self):
        self.generate_challenge()

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
        service = self.get_whatsapp_service()
        return service.confirmed if service else False

    def get_whatsapp_service(self):
        whatsapp = getattr(self, 'whatsapp', None)

        try:
            service = WhatsappService.objects.get(user=self, whatsapp=whatsapp)
        except WhatsappService.DoesNotExist:
            service = None

        return service

    def check_whatsapp_passcode(self, passcode):
        if getattr(self, 'whatsapp', None):
            service = self.get_whatsapp_service()

            if not service:
                return False

            return service.check_passcode(passcode) if passcode else False

    def verify_whatsapp(self, request=None):
        if getattr(self, 'whatsapp', None):
            service = self.get_whatsapp_service()

            if not service:
                service = WhatsappService(
                    user=self,
                    name='default', # temporal
                    whatsapp=self.whatsapp,
                    key=random_hex(20), # OBSOLETED: .decode('ascii'),
                    confirmed=False,
                )

                service.save()

            service.generate_challenge(request)
            return service

    def verify(self, request=None):
        super().verify(request)

        if self.whatsapp and not self.is_whatsapp_confirmed:
            self.verify_whatsapp(request)
