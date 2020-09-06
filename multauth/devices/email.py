from django.db import models
from django.core import signing
from django.urls import reverse
# RESERVED # from django.urls.exceptions import NoReverseMatch
from django.contrib.auth.hashers import check_password, is_password_usable, make_password
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from django_otp.util import random_hex

from .abstract import AbstractDevice, AbstractUserMixin, PASSCODE_EXPIRY


try:
    EmailProvider = settings.MULTAUTH_DEVICE_EMAIL_PROVIDER
except AttributeError:
    from ..providers.mail import MailProvider
    EmailProvider = MailProvider


DEBUG = getattr(settings, 'DEBUG', False)
MULTAUTH_DEBUG = getattr(settings, 'MULTAUTH_DEBUG', DEBUG)
MULTAUTH_CONFIRMED = getattr(settings, 'MULTAUTH_DEVICE_EMAIL_CONFIRMED', True)
MULTAUTH_TEMPLATE_NAME = getattr(settings, 
    'MULTAUTH_DEVICE_EMAIL_TEMPLATE_NAME', 'email'
)
MULTAUTH_VERIFICATION_VIEWNAME = getattr(settings,
    'MULTAUTH_DEVICE_EMAIL_VERIFICATION_VIEWNAME',
    'multauth:signup-verification-email-key'
)

TEMPLATE_SUBJECT_SUFFIX = '_subject.txt'
TEMPLATE_BODY_SUFFIX = '_body.txt'
TEMPLATE_BODY_HTML_SUFFIX = '_body.html'


# TODO: reset token when "confirmed" updated?
class EmailDevice(AbstractDevice):
    email = models.EmailField(unique=True)
    confirmed = models.BooleanField(default=MULTAUTH_CONFIRMED) # override parent
    # reserved # hardcode = models.CharField(max_length=128) # experimental

    USER_MIXIN = 'EmailUserMixin'
    IDENTIFIER_FIELD = 'email'

    def __eq__(self, other):
        if not isinstance(other, EmailDevice):
            return False

        return self.email == other.email \
            and self.key == other.key

    def __hash__(self):
        return hash((self.email,))

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
            device = EmailDevice.objects.get(email=email)

        except (signing.SignatureExpired, signing.BadSignature, EmailDevice.DoesNotExist):
            device = None

        return device

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
        device = self.get_email_device()
        return device.confirmed if device else False

    def clean(self):
        super().clean()

        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)

    def get_email_device(self):
        email = getattr(self, 'email', '')

        try:
            device = EmailDevice.objects.get(user=self, email=email)
        except EmailDevice.DoesNotExist:
            device = None

        return device

    def email_user(self, subject, message, from_email=None, **kwargs):
        device = self.get_email_device()
        device.send(
            to=self.email,
            subject=subject,
            message=message,
            **kwargs,
        )

    def verify_email(self, request=None):
        if getattr(self, 'email', None):
            device = self.get_email_device()

            if not device:
                device = EmailDevice(
                    user=self,
                    name='default', # temporal
                    email=self.email,
                    key=random_hex(20), # OBSOLETED: .decode('ascii'),
                    confirmed=False,
                )

                device.save()

            device.generate_challenge(request)
            return device

    def verify_email_token(self, token):
        if getattr(self, 'email', None):
            device = self.get_email_device()

            if not device:
                return False

            return device.verify_token(token) if token else False

    # RESERVED
    # @classmethod
    # def verify_email_token(cls, email, token):
    #     try:
    #         device = EmailDevice.objects.get(email=email)
    #     except:
    #         return None

    #     return device.user if device.verify_token(token) else None

    @classmethod
    def verify_email_key(cls, key):
        device = EmailDevice.verify_key(key)
        return device.user if device else None

    def verify(self, request=None):
        super().verify(request)

        if self.email and not self.is_email_confirmed:
            self.verify_email(request)
