from django.conf import settings
from boto3 import Session

from .abstract import AbstractProvider


AMAZON_API_KEY = getattr(settings, 'MULTAUTH_PROVIDER_AMAZON_API_KEY', None)
AMAZON_API_SECRET = getattr(settings, 'MULTAUTH_PROVIDER_AMAZON_API_SECRET', None)
amazon_from = getattr(settings, 'MULTAUTH_PROVIDER_AMAZON_BRAND_NAME', None)

if AMAZON_API_KEY:
    client = Client(key=AMAZON_API_KEY, secret=AMAZON_API_SECRET)
else:
    print('Amazon: running in mock mode. Set "account sid" and other params.')
    client = None


class AmazonProvider(AbstractProvider):

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
                'from': amazon_from,
                'text': self.message,
            })

            # todo:
            # catch errors in response
            # {'message-count': '1', 'messages': [{'status': '2', 'error-text': 'Missing Message Text'}]}
        else:
            print('Amazon: to %s, message "%s"' % (self.to, self.message))
