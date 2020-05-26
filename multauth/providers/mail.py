from django.core.mail import send_mail
from django.conf import settings

from .abstract import AbstractProvider


mail_from = getattr(settings, 'DEFAULT_FROM_EMAIL', None)


class MailProvider(AbstractProvider):

    def __init__(self, to, subject='', message='', is_html=False, *args, **kwargs):
        """
        Args:
        @to (str)
        @subject (str)
        @message (str)
        @is_html (str): optional
        @fail_silently (bool): optional
        """
        self.to = to
        self.subject = subject
        self.message = message
        self.is_html = is_html
        # RESERVED # self.fail_silently = kwargs.get('fail_silently', False)

    def send(self):
        # RESERVED
        # if celery:
        #     send_task.delay(self)
        # else:
        #     self._send()
        self._send()

    def _send(self):
        if not self.to:
            return

        send_mail(self.subject, self.message, mail_from, [self.to],
            html_message=self.message if self.is_html else None) # RESERVED # fail_silently=self.fail_silently
