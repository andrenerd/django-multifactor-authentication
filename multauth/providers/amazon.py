from django.conf import settings
from boto3 import Session

from .abstract import AbstractProvider

# reserved # amazon_from = getattr(settings, 'MULTAUTH_PROVIDER_AMAZON_BRAND_NAME', None)

# todo: check Session
if True:
    client = Session().client('sns')
else:
    print('Amazon: running in mock mode. Set "account sid" and other params.')
    client = None


# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.publish
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
            try:
                client.publish(
                    PhoneNumber=self.to,
                    Message=self.message,
                )

            except Exception as e:
                # todo:
                # specify catcher and created exception
                raise

        else:
            print('Amazon: to %s, message "%s"' % (self.to, self.message))
