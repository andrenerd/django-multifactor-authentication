from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.hashers import check_password, make_password

# OBSOLETED # from django_otp import match_token
from django_otp.util import random_hex
from phonenumber_field.modelfields import PhoneNumberField

from .devices import PhoneDevice, EmailDevice
from .managers import UserManager


class AbstractUser(AbstractBaseUser, PermissionsMixin):

    phone = PhoneNumberField(_('Phone number'), blank=True, null=True, unique=True,
        #help_text = _('Required.'),
        error_messages = {
            'unique': _('A user with that phone number already exists.'),
        }
    )
    passcode = models.CharField(_('Passcode'), max_length=128) # editable=False

    email = models.EmailField(_('Email address'), blank=True, null=True, unique=True,
        #help_text = _('Required.'),
        error_messages = {
            'unique': _('A user with that email address already exists.'),
        }
    )
    # password

    username = models.CharField(_('Username'), max_length=64, editable=False, unique=True)
    first_name = models.CharField(_('First name'), max_length=30, null=True, blank=True)
    last_name = models.CharField(_('Last name'), max_length=150, null=True, blank=True)

    is_staff = models.BooleanField(_('Staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(_('Active'), default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_phone_verified = models.BooleanField(_('Phone verified'), default=False,
        help_text=_('Designates whether this user phone is verified.'),
    )
    is_email_verified = models.BooleanField(_('Email verified'), default=False,
        help_text=_('Designates whether this user email is verified.'),
    )
    date_joined = models.DateTimeField(_('Date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return '%s (%s)' % (self.get_full_name(), self.phone or self.email)

    def clean(self):
        super().clean()

        phone = getattr(self, 'phone', None)
        email = getattr(self, 'email', None)

        if not phone and not email:
            raise ValidationError('At least one of the identifiers (phone, email) must be set')

        if email:
            self.email = self.__class__.objects.normalize_email(self.email)

    def save(self, *args, **kwargs):
        self.create_username()
        super().save(*args, **kwargs)

    def create_username(self):
        max_length = self._meta.get_field('username').max_length

        setattr(self, 'username', self.normalize_username('%s%s' % (
            getattr(self, 'email', ''), getattr(self, 'phone', '')
        ))[:max_length - 1])

    def get_username(self):
        return str(getattr(self, self.USERNAME_FIELD))

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def get_phone_device(self):
        phone = getattr(self, 'phone', None)

        try: 
            device = PhoneDevice.objects.get(user=self, phone=phone)
        except PhoneDevice.DoesNotExist:
            device = None

        return device

    def get_email_device(self):
        email = getattr(self, 'email', None)

        try: 
            device = EmailDevice.objects.get(user=self, email=email)
        except EmailDevice.DoesNotExist:
            device = None

        return device

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def verify(self, request=None):
        if self.phone and not self.is_phone_verified:
            self.verify_phone(request)

        if self.email and not self.is_email_verified:
            self.verify_email(request)

    def verify_phone(self, request=None):
        if getattr(self, 'phone', None):
            device = self.get_phone_device()

            if not device:
                device = PhoneDevice(
                    user=self,
                    name='default', # temporal
                    phone=self.phone,
                    key=random_hex(20).decode('ascii'),
                    confirmed=False,
                )

                device.save()

            device.generate_challenge(request)
            return device

    def verify_phone_token(self, token):
        if getattr(self, 'phone', None):
            device = self.get_phone_device()

            if not device:
                return False

            return device.verify_token(token) if token else False

    def verify_email(self, request=None):
        if getattr(self, 'email', None):
            device = self.get_email_device()

            if not device:
                device = EmailDevice(
                    user=self,
                    name='default', # temporal
                    email=self.email,
                    key=random_hex(20).decode('ascii'),
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

    def set_passcode(self, raw_passcode):
        self.passcode = make_password(raw_passcode)
        self._passcode = raw_passcode

    def check_passcode(self, raw_passcode):
        """
        Return a boolean of whether the raw_passcode was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_passcode):
            self.set_passcode(raw_passcode)

            # Password hash upgrades shouldn't be considered passcode changes.
            self._passcode = None
            self.save(update_fields=['passcode'])

        return check_password(raw_passcode, self.passcode, setter)

    def set_unusable_passcode(self):
        # Set a value that will never be a valid hash
        self.passcode = make_password(None)

    def has_usable_passcode(self):
        """
        Return False if set_unusable_passcode() has been called for this user.
        """
        return is_passcode_usable(self.passcode)


def groups_add(self, name):
    """
    Custom helper method for User class to add group(s).
    """
    group, _ = Group.objects.get_or_create(name=name)
    group.user_set.add(self)

    return self


def groups_remove(self, name):
    """
    Custom helper method for User class to remove group(s).
    """
    group, _ = Group.objects.get_or_create(name=name)
    group.user_set.remove(self)

    return self


@property
def is_admin(self):
    """
    Custom helper method for User class to check user type/profile.
    """
    if not hasattr(self, '_is_admin'):
        self._is_admin = self.groups.filter(name=get_user_model().GROUP_ADMIN).exists()

    return self._is_admin


# EXAMPLE
# @property
# def is_custom_user(self):
#     """
#     Custom helper method for User class to check user type/profile.
#     """
#     if not hasattr(self, '_is_custom_user'):
#         self._is_custom_user = self.groups.filter(name=get_user_model().GROUP_CUSTOM_USER).exists()

#     return self._is_custom_user


# Add custom methods to User class
get_user_model().add_to_class('groups_add', groups_add)
get_user_model().add_to_class('groups_remove', groups_remove)

get_user_model().add_to_class('is_admin', is_admin) # EXAMPLE
# get_user_model().add_to_class('is_custom_user', is_custom_user) # EXAMPLE

get_user_model().add_to_class('GROUP_ADMIN', 'Admins')
# get_user_model().add_to_class('GROUP_CUSTOM_USER', 'CustomUsers') # EXAMPLE


get_user_model().add_to_class('PROFILES', {
    # get_user_model().GROUP_CUSTOM_USER: {'app_label': 'custom', 'model_name': 'CustomUser'},
})


from . import connectors # just to init all the connectors, don't remove it
