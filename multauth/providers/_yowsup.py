from django.conf import settings
from yowsup.rest import Client

from .abstract import AbstractProvider


YOWSUP_ACCOUNT_SID = getattr(settings, 'MULTAUTH_PROVIDER_YOWSUP_ACCOUNT_SID', None)
YOWSUP_AUTH_TOKEN = getattr(settings, 'MULTAUTH_PROVIDER_YOWSUP_AUTH_TOKEN', None)
yowsup_from = getattr(settings, 'MULTAUTH_PROVIDER_YOWSUP_CALLER_ID', None)
# yowsup_whatsapp_prefix = 'whatsapp:'

# see
# https://github.com/tgalal/yowsup
if YOWSUP_ACCOUNT_SID:
    client = Client(YOWSUP_ACCOUNT_SID, YOWSUP_AUTH_TOKEN)
else:
    print('Yowsup: running in mock mode. Set "account sid" and other params.')
    client = None


class YowsupProvider(AbstractProvider):

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
    # https://github.com/tgalal/yowsup
    def _send(self):
        if not self.to:
            return

        if client:
            client.messages.create(
                to=self.to,
                from_=from_,
                body=self.message,
            )
        else:
            print('Yowsup: to %s, message "%s"' % (self.to, self.message))
