from django.conf import settings
from telethon import TelegramClient
import telebot 

from .abstract import AbstractProvider


TELEGRAM_API_ID = getattr(settings, 'MULTAUTH_PROVIDER_TELEGRAM_API_ID', None)
TELEGRAM_API_HASH = getattr(settings, 'MULTAUTH_PROVIDER_TELEGRAM_API_HASH', None)
TELEGRAM_BOT_TOKEN = getattr(settings, 'MULTAUTH_PROVIDER_TELEGRAM_BOT_TOKEN', None)
telegram_from = getattr(settings, 'MULTAUTH_PROVIDER_TELEGRAM_CALLER_ID', None)
telegram_whatsapp_prefix = 'whatsapp:'

# see
# https://core.telegram.org/api/obtaining_api_id
if TELEGRAM_API_ID:
    client = TelegramClient('session', TELEGRAM_API_ID, TELEGRAM_API_HASH) 
else:
    print('Telegram: running in mock mode. Set "api id" and other params.')
    client = None


class TelegramProvider(AbstractProvider):

    def __init__(self, to, message='', *args, **kwargs):
        """
        Args:
        @to (str)
        @message (str)
        @fail_silently (bool): optional
        """
        self.to = to
        self.message = message
        # RESERVED # self.fail_silently = kwargs.get('fail_silently', False)

    # todo:
    # handle exceptions
    # https://github.com/telegram/telegram-python/#handling-exceptions
    def _send(self):
        if not self.to:
            return

        if client:
            # experimental
            if self.to.startswith(telegram_whatsapp_prefix): 
                from_ = telegram_whatsapp_prefix + telegram_from
            else:
                from_ = telegram_from

            client.messages.create(
                to=self.to,
                from_=from_,
                body=self.message,
            )
        else:
            print('Telegram: to %s, message "%s"' % (self.to, self.message))
