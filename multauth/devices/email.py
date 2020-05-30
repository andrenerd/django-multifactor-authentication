from django.db import models
from django.core import signing
from django.urls import reverse
# RESERVED # from django.urls.exceptions import NoReverseMatch
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
    'multauth:signup-verification-email-key')

TEMPLATE_SUBJECT_SUFFIX = '_subject.txt'
TEMPLATE_BODY_SUFFIX = '_body.txt'
TEMPLATE_BODY_HTML_SUFFIX = '_body.html'


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

            subject = self._render_subject(context)
            body = self._render_body(context)

            if body:
                MailProvider(
                    to=self.email,
                    subject=subject,
                    message=body,
                    is_html=self._template_body_is_html,
                ).send()

    @classmethod
    def verify_key(cls, key):
        try:
            email = signing.loads(key, max_age=TOKEN_EXPIRY, salt=settings.SECRET_KEY)
            device = EmailDevice.objects.get(email=email)

        except (signing.SignatureExpired, signing.BadSignature, EmailDevice.DoesNotExist):
            device = None

        return device

    def _render_subject(self, context):
        if hasattr(self, '_template_subject'):
            return self._render_template(self._template_subject, context)

        else:
            try:
                TEMPLATE_SUBJECT = get_template('multauth/' + MULTAUTH_TEMPLATE_NAME + TEMPLATE_SUBJECT_SUFFIX)
            except (TemplateDoesNotExist, TemplateSyntaxError):
                if DEBUG: raise TemplateDoesNotExist('Template: {}' \
                    .format(MULTAUTH_TEMPLATE_NAME + TEMPLATE_SUBJECT_SUFFIX))
                TEMPLATE_SUBJECT = None

            self._template_subject = TEMPLATE_SUBJECT
            return self._render_template(self._template_subject, context)

    def _render_body(self, context):
        if hasattr(self, '_template_body'):
            return self._render_template(self._template_body, context)

        else:
            try:
                TEMPLATE_BODY = get_template('multauth/' + MULTAUTH_TEMPLATE_NAME + TEMPLATE_BODY_HTML_SUFFIX)
                TEMPLATE_BODY_IS_HTML = True
            except (TemplateDoesNotExist, TemplateSyntaxError):
                try:
                    TEMPLATE_BODY = get_template('multauth/' + MULTAUTH_TEMPLATE_NAME + TEMPLATE_BODY_SUFFIX)
                except (TemplateDoesNotExist, TemplateSyntaxError):
                    if DEBUG: raise TemplateDoesNotExist('Template: {}' \
                        .format(MULTAUTH_TEMPLATE_NAME + TEMPLATE_BODY_SUFFIX))
                    TEMPLATE_BODY = None
                finally:
                    TEMPLATE_BODY_IS_HTML = False

            self._template_body = TEMPLATE_BODY
            self._template_body_is_html = TEMPLATE_BODY_IS_HTML
            return self._render_template(self._template_body, context)

    def  _render_template(self, template, context):
        if template:
            return _(template.render(context)).strip()
        else:
            return None
