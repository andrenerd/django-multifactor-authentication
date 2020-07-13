from django.conf import settings

from .abstract import AbstractProvider


class BillProvider(AbstractProvider):

    def __init__(self, to, message='', *args, **kwargs):
        """
        Args:
        @to (str)
        @message (str)
        """
        raise NotImplementedError('Not implemented yet. Please create an issue in the repo')

    def _send(self):
        pass
