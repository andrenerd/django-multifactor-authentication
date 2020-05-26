from django.db import models
from django.core import signing
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .abstract import AbstractDevice, TOKEN_EXPIRY
from ..providers import MailProvider


MailProvider = getattr(settings, 'MULTAUTH_EMAIL_PROVIDER', MailProvider)


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)
MULTAUTH_TEMPLATE_NAME = getattr(settings, 'MULTAUTH_EMAIL_TEMPLATE_NAME', 'email')
MULTAUTH_VERIFICATION_VIEWNAME = getattr(settings, 'MULTAUTH_EMAIL_VERIFICATION_VIEWNAME',
    'api:signup-verification-email-key')

TEMPLATE_SUBJECT_SUFFIX = '_subject.txt'
TEMPLATE_MESSAGE_SUFFIX = '_body.txt'
TEMPLATE_MESSAGE_HTML_SUFFIX = '_body.html'


try:
    SUBJECT_TEMPLATE = get_template(MULTAUTH_TEMPLATE_NAME + TEMPLATE_SUBJECT_SUFFIX)
except (TemplateDoesNotExist, TemplateSyntaxError):
    if DEBUG: raise TemplateDoesNotExist('Template: {}'.format(MULTAUTH_TEMPLATE_NAME))
    SUBJECT_TEMPLATE = None

try:
    MESSAGE_TEMPLATE = get_template(MULTAUTH_TEMPLATE_NAME + TEMPLATE_MESSAGE_HTML_SUFFIX)
    MESSAGE_TEMPLATE_IS_HTML = True
except (TemplateDoesNotExist, TemplateSyntaxError):
    try:
        MESSAGE_TEMPLATE = get_template(MULTAUTH_TEMPLATE_NAME + TEMPLATE_MESSAGE_SUFFIX)
    except (TemplateDoesNotExist, TemplateSyntaxError):
        if DEBUG: raise TemplateDoesNotExist('Template: {}'.format(MULTAUTH_TEMPLATE_NAME))
        MESSAGE_TEMPLATE = None
    finally:
        MESSAGE_TEMPLATE_IS_HTML = False


class EmailDevice(AbstractDevice):
    """
    Model with email address and token seed linked to a user.
    """
    email = models.EmailField()

    def __eq__(self, other):
        if not isinstance(other, EmailDevice):
            return False

        return self.email == other.email \
            and self.key == other.key

    def __hash__(self):
        return hash((self.email,))

    def generate_challenge(self, request=None):
        token = self.get_token()
        key = signing.dumps(self.email, salt=settings.SECRET_KEY) # for verification url only
        path = reverse(MULTAUTH_VERIFICATION_VIEWNAME, args=[key]) # yes, key. not token

        if MULTAUTH_DEBUG:
            print('Fake auth message, email: %s, token: %s ' % (self.email, token))

        else:
            context = {
                'full_name': self.user.get_full_name(),
                'url': (
                        (request.scheme or 'http') +
                        '://' + str(get_current_site(request)) +
                        path
                    ) if request else None,
                'token': token,
            }

            subject = _(SUBJECT_TEMPLATE.render(context)) if SUBJECT_TEMPLATE else None
            message = _(MESSAGE_TEMPLATE.render(context)) if MESSAGE_TEMPLATE else None

            if message:
                MailProvider(
                    to=self.email,
                    subject=subject.strip(),
                    message=message.strip(),
                    is_html=MESSAGE_TEMPLATE_IS_HTML,
                ).send()

    @classmethod
    def verify_key(cls, key):
        try:
            email = signing.loads(key, max_age=TOKEN_EXPIRY, salt=settings.SECRET_KEY)
            device = EmailDevice.objects.get(email=email)

        except (signing.SignatureExpired, signing.BadSignature, EmailDevice.DoesNotExist):
            device = None

        return device
