from django.db import models
from django.core import signing
from django.urls import reverse
from django.utils.module_loading import import_string
from django.contrib.auth.hashers import check_password, is_password_usable, make_password
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from django_otp.util import random_hex

from .abstract import AbstractService, PasscodeServiceMixin, AbstractUserMixin
from .abstract import PASSCODE_EXPIRY


try:
    EmailProviderPath = settings.MULTAUTH_SERVICE_EMAIL_PROVIDER
    EmailProvider = import_string(EmailProviderPath) # ex. multauth.providers.MailProvider
except AttributeError:
    from ..providers.mail import MailProvider
    EmailProvider = MailProvider


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)
MULTAUTH_CONFIRMED = getattr(settings, 'MULTAUTH_SERVICE_EMAIL_CONFIRMED', True)
MULTAUTH_TEMPLATE_NAME = getattr(settings, 
    'MULTAUTH_SERVICE_EMAIL_TEMPLATE_NAME', 'email'
)
MULTAUTH_VERIFICATION_VIEWNAME = getattr(settings,
    'MULTAUTH_SERVICE_EMAIL_VERIFICATION_VIEWNAME',
    'multauth:signup-verification-email-key'
)

TEMPLATE_SUBJECT_SUFFIX = '_subject.txt'
TEMPLATE_BODY_SUFFIX = '_body.txt'
TEMPLATE_BODY_HTML_SUFFIX = '_body.html'


# TODO: reset token when "confirmed" updated?
class EmailService(PasscodeServiceMixin, AbstractService):
    email = models.EmailField(unique=True)
    confirmed = models.BooleanField(default=MULTAUTH_CONFIRMED) # override parent

    USER_MIXIN = 'EmailUserMixin'
    IDENTIFIER_FIELD = 'email'

    def __eq__(self, other):
        if not isinstance(other, EmailService):
            return False

        return self.email == other.email \
            and self.key == other.key

    def __hash__(self):
        return hash((self.email,))

    def set_passcode(self):
        self.generate_challenge()

    def generate_challenge(self, request=None):
        self.generate_token()
        key = signing.dumps(self.email, salt=settings.SECRET_KEY) # for verification url only
        path = reverse(MULTAUTH_VERIFICATION_VIEWNAME, args=[key]) # yes, key. not token

        if MULTAUTH_DEBUG:
            print('Fake auth message, email: %s, token: %s ' % (self.email, self.token))

        # TODO: think to replace: "request.scheme or 'http"
        else:
            context = {
                'full_name': self.user.get_full_name(),
                'url': (
                        (request.scheme or 'http') +
                        '://' + str(get_current_site(request)) +
                        path
                    ) if request else None,
                'token': self.token,
            }

            subject = self._render_subject(context)
            body = self._render_body(context)

            if body:
                EmailProvider(
                    to=self.email,
                    subject=subject,
                    message=body,
                    is_html=self._template_body_is_html,
                ).send()

        return self.token

    @classmethod
    def verify_key(cls, key):
        try:
            email = signing.loads(key, max_age=PASSCODE_EXPIRY, salt=settings.SECRET_KEY)
            service = EmailService.objects.get(email=email)

        except (signing.SignatureExpired, signing.BadSignature, EmailService.DoesNotExist):
            service = None

        return service

    def _render_subject(self, context):
        if hasattr(self, '_template_subject'):
            return self._render_template(self._template_subject, context)

        else:
            try:
                TEMPLATE_SUBJECT = get_template('multauth/'
                    + MULTAUTH_TEMPLATE_NAME
                    + TEMPLATE_SUBJECT_SUFFIX
                )

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
                TEMPLATE_BODY = get_template('multauth/'
                    + MULTAUTH_TEMPLATE_NAME
                    + TEMPLATE_BODY_HTML_SUFFIX
                )
                TEMPLATE_BODY_IS_HTML = True

            except (TemplateDoesNotExist, TemplateSyntaxError):
                try:
                    TEMPLATE_BODY = get_template('multauth/'
                        + MULTAUTH_TEMPLATE_NAME
                        + TEMPLATE_BODY_SUFFIX
                    )

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


class EmailUserMixin(AbstractUserMixin):

    email = models.EmailField(_('Email address'), blank=True, null=True, unique=True,
        # help_text = _('Required.'),
        error_messages = {
            'unique': _('A user with that email address already exists.'),
        }
    )

    EMAIL_FIELD = 'email'

    class Meta:
        abstract = True

    def __str__(self):
        return str(getattr(self, 'email'))

    @property
    def is_email_confirmed(self):
        service = self.get_email_service()
        return service.confirmed if service else False

    def clean(self):
        super().clean()

        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)

    def get_email_service(self):
        email = getattr(self, 'email', '')

        try:
            service = EmailService.objects.get(user=self, email=email)
        except EmailService.DoesNotExist:
            service = None

        return service

    def check_email_passcode(self, passcode):
        if getattr(self, 'email', None):
            service = self.get_email_service()

            if not service:
                return False

            return service.check_passcode(passcode) if passcode else False

    def email_user(self, subject, message, from_email=None, **kwargs):
        service = self.get_email_service()
        service.send(
            to=self.email,
            subject=subject,
            message=message,
            **kwargs,
        )

    def verify_email(self, request=None):
        if getattr(self, 'email', None):
            service = self.get_email_service()

            if not service:
                service = EmailService(
                    user=self,
                    name='default', # temporal
                    email=self.email,
                    key=random_hex(20), # OBSOLETED: .decode('ascii'),
                    confirmed=False,
                )

                service.save()

            service.generate_challenge(request)
            return service

    @classmethod
    def verify_email_key(cls, key):
        service = EmailService.verify_key(key)
        return service.user if service else None

    def verify(self, request=None):
        super().verify(request)

        if self.email and not self.is_email_confirmed:
            self.verify_email(request)
