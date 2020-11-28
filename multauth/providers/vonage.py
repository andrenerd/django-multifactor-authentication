from django.conf import settings
from vonage import Client, Sms

from .abstract import AbstractProvider


VONAGE_API_KEY = getattr(settings, 'MULTAUTH_PROVIDER_VONAGE_API_KEY', None)
VONAGE_API_SECRET = getattr(settings, 'MULTAUTH_PROVIDER_VONAGE_API_SECRET', None)
vonage_from = getattr(settings, 'MULTAUTH_PROVIDER_VONAGE_BRAND_NAME', None)

# see
# https://github.com/vonage/vonage-python-sdk
if VONAGE_API_KEY:
    client = Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
else:
    print('Vonage: running in mock mode. Set "account sid" and other params.')
    client = None


class VonageProvider(AbstractProvider):

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

    def _send(self):
        if not self.to:
            return

        if client:
            sms = Sms(client)
            response = sms.send_message({
                'to': self.to,
                'from': vonage_from,
                'text': self.message,
            })

            # todo:
            # catch errors in response
            # {'message-count': '1', 'messages': [{'status': '2', 'error-text': 'Missing Message Text'}]}
        else:
            print('Vonage: to %s, message "%s"' % (self.to, self.message))
