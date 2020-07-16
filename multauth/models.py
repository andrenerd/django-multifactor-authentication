from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.validators import UnicodeUsernameValidator

# OBSOLETED # from django_otp import match_token
from django_otp.util import random_hex
from phonenumber_field.modelfields import PhoneNumberField

from .managers import UserManager
from .mixins import UserDevicesMixin


class AbstractUser(AbstractBaseUser, UserDevicesMixin, PermissionsMixin):

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(_('username'), max_length=150, unique=True, # editable=False
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

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

    date_joined = models.DateTimeField(_('Date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [] # TODO: fill with identifiers and more

    class Meta:
        abstract = True
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return '{0} ({1})'.format(
            self.get_full_name() or 'Noname',
            ', '.join(self.get_devices_names()) or '-', # experimental
        ).strip()

    def clean(self):
        super().clean()

        # TODO / TEMP: replace / move to mixins.py
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

        # TODO / TEMP: replace / move to mixins.py
        setattr(self, 'username', self.normalize_username('%s%s' % (
            getattr(self, 'email', ''), getattr(self, 'phone', '')
        ))[:max_length - 1])

    def get_username(self):
        return str(getattr(self, self.USERNAME_FIELD))

    def get_full_name(self):
        return '{0} {1}'.format(self.first_name or '', self.last_name or '').strip()

    def get_short_name(self):
        return self.first_name

    # OBSOLETED: refactored. see DevicesMixin
    # def verify(self, request=None):
    #     if self.phone and not self.is_phone_verified:
    #         self.verify_phone(request)

    #     if self.email and not self.is_email_verified:
    #         self.verify_email(request)


class User(AbstractUser):

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'


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
