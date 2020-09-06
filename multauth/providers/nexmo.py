from django.conf import settings
# from nexmo.rest import Client

from .abstract import AbstractProvider


# nexmo = Client(
#     getattr(settings, 'MULTAUTH_PROVIDER_NEXMO_ACCOUNT_SID', None)
#     getattr(settings, 'MULTAUTH_PROVIDER_NEXMO_AUTH_TOKEN', None)
# )

# nexmo_from = getattr(settings, 'MULTAUTH_PROVIDER_NEXMO_CALLER_ID', None)


class NexmoProvider(AbstractProvider):

    def __init__(self, to, message='', *args, **kwargs):
        """
        Args:
        @to (str)
        @message (str)
        @fail_silently (bool): optional
        """
        raise NotImplementedError('Not implemented yet. Please create an issue in the repo')
        # self.to = to
        # self.message = message
        # RESERVED # self.fail_silently = kwargs.get('fail_silently', False)

    def _send(self):
        pass

        # if not self.to:
        #     return