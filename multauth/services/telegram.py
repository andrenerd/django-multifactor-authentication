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
    TelegramProviderPath = settings.MULTAUTH_SERVICE_TELEGRAM_PROVIDER
    TelegramProvider = import_string(TelegramProviderPath) # ex. multauth.providers.TelegramProvider
except AttributeError:
    from ..providers.telegram import TelegramProvider


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)
MULTAUTH_CONFIRMED = getattr(settings, 'MULTAUTH_SERVICE_TELEGRAM_CONFIRMED', True)
MULTAUTH_TEMPLATE_NAME = getattr(settings, 'MULTAUTH_SERVICE_TELEGRAM_TEMPLATE_NAME', 'telegram')

TEMPLATE_MESSAGE_SUFFIX = '.txt'


class TelegramService(PasscodeServiceMixin, AbstractService):
    telegram = PhoneNumberField(unique=True)
    confirmed = models.BooleanField(default=MULTAUTH_CONFIRMED) # override parent

    USER_MIXIN = 'TelegramUserMixin'
    IDENTIFIER_FIELD = 'telegram'

    def __eq__(self, other):
        if not isinstance(other, TelegramService):
            return False

        return self.telegram == other.telegram \
            and self.key == other.key

    def __hash__(self):
        return hash((self.telegram,))

    def clean(self):
        super().clean()

    def set_passcode(self):
        self.generate_challenge()

    def generate_challenge(self, request=None):
        self.generate_token()

        if MULTAUTH_DEBUG:
            print('Fake auth message, telegram: %s, token: %s ' % (self.telegram, self.token))

        else:
            context = {
                'token': self.token,
            }

            message = self._render_message(context)

            if message:
                TelegramProvider(
                    to=self.telegram.as_e164,
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


class TelegramUserMixin(AbstractUserMixin):

    telegram = PhoneNumberField(_('Telegram identifier'), blank=True, null=True, unique=True,
        # help_text = _('Required.'),
        error_messages = {
            'unique': _('A user with that Telegram identifier already exists.'),
        }
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(getattr(self, 'telegram', ''))

    @property
    def is_telegram_confirmed(self):
        service = self.get_telegram_service()
        return service.confirmed if service else False

    def get_telegram_service(self):
        telegram = getattr(self, 'telegram', None)

        try:
            service = TelegramService.objects.get(user=self, telegram=telegram)
        except TelegramService.DoesNotExist:
            service = None

        return service

    def check_telegram_passcode(self, passcode):
        if getattr(self, 'telegram', None):
            service = self.get_telegram_service()

            if not service:
                return False

            return service.check_passcode(passcode) if passcode else False

    def verify_telegram(self, request=None):
        if getattr(self, 'telegram', None):
            service = self.get_telegram_service()

            if not service:
                service = TelegramService(
                    user=self,
                    name='default', # temporal
                    telegram=self.telegram,
                    key=random_hex(20), # OBSOLETED: .decode('ascii'),
                    confirmed=False,
                )

                service.save()

            service.generate_challenge(request)
            return service

    def verify(self, request=None):
        super().verify(request)

        if self.telegram and not self.is_telegram_confirmed:
            self.verify_telegram(request)
