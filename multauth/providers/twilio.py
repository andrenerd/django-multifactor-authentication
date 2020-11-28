from django.conf import settings
from twilio.rest import Client

from .abstract import AbstractProvider


TWILIO_ACCOUNT_SID = getattr(settings, 'MULTAUTH_PROVIDER_TWILIO_ACCOUNT_SID', None)
TWILIO_AUTH_TOKEN = getattr(settings, 'MULTAUTH_PROVIDER_TWILIO_AUTH_TOKEN', None)
twilio_from = getattr(settings, 'MULTAUTH_PROVIDER_TWILIO_CALLER_ID', None)

# see
# https://www.twilio.com/docs/libraries/python
# https://github.com/twilio/twilio-python/
if TWILIO_ACCOUNT_SID:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    print('Twilio: running in mock mode. Set "account sid" and other params.')
    client = None


class TwilioProvider(AbstractProvider):

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
    # https://github.com/twilio/twilio-python/#handling-exceptions
    def _send(self):
        if not self.to:
            return

        if client:
            client.messages.create(
                to=self.to,
                from_=twilio_from,
                body=self.message,
            )
        else:
            print('Twilio: to %s, message "%s"' % (self.to, self.message))
