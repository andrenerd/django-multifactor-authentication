from django.core.mail import send_mail
from django.conf import settings

from twilio.rest import Client

from .abstract import AbstractProvider


twilio = Client(
    getattr(settings, 'MULTAUTH_PROVIDER_TWILIO_ACCOUNT_SID', None),
    getattr(settings, 'MULTAUTH_PROVIDER_TWILIO_AUTH_TOKEN', None)
)

twilio_from = getattr(settings, 'MULTAUTH_PROVIDER_TWILIO_CALLER_ID', None)


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

    def _send(self):
        if not self.to:
            return

        twilio.messages.create(
            to=self.to,
            from_=twilio_from,
            body=self.message,
        )
