from django.conf import settings
from vonage.rest import Client, Sms

from .abstract import AbstractProvider


VONAGE_API_KEY = getattr(settings, 'MULTAUTH_PROVIDER_VONAGE_API_KEY', None)
VONAGE_API_SECRET = getattr(settings, 'MULTAUTH_PROVIDER_VONAGE_API_SECRET', None)
vonage_from = getattr(settings, 'MULTAUTH_PROVIDER_VONAGE_BRAND_NAME', None)

# see
# https://github.com/vonage/vonage-python-sdk
if VONAGE_API_KEY:
    vonage = Client(key=TWILIO_ACCOUNT_SID, secret=TWILIO_AUTH_TOKEN)
    sms = Sms(client)
else:
    print('Vonage: running in mock mode. Set "account sid" and other params.')
    vonage = None


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

        if vonage:
            sms.send_message({
                'to': self.to,
                'from': vonage_from,
                'body': self.message,
            })
        else:
            print('Vonage: to %s, message "%s"' % (self.to, self.message))
