from django.conf import settings
from telethon.sync import TelegramClient
# import telebot # todo: is it really needed?

from .abstract import AbstractProvider


TELEGRAM_API_ID = getattr(settings, 'MULTAUTH_PROVIDER_TELEGRAM_API_ID', None)
TELEGRAM_API_HASH = getattr(settings, 'MULTAUTH_PROVIDER_TELEGRAM_API_HASH', None)
TELEGRAM_BOT_TOKEN = getattr(settings, 'MULTAUTH_PROVIDER_TELEGRAM_BOT_TOKEN', None)
telegram_from = getattr(settings, 'MULTAUTH_PROVIDER_TELEGRAM_CALLER_ID', None)

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
    def _send(self):
        if not self.to:
            return

        if client:
            client.connect()

            if not client.is_user_authorized():
                client.sign_in(bot_token=TELEGRAM_BOT_TOKEN)

            try:
                client.send_message(self.to, self.message)
            except Exception as e:
                pass

            client.disconnect() 

        else:
            print('Telegram: to %s, message "%s"' % (self.to, self.message))
