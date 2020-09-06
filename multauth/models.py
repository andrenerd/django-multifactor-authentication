from functools import reduce
from django_otp import match_token

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, AbstractBaseUser, PermissionsMixin
from django.conf import settings

from .managers import UserManager
from .mixins import UserDevicesMixin

# TODO: add MULTAUTH_ACTIVATED, as default 'is_active' field value
# RESERVED # PASSWORD, PASSCODE, HARDCODE = 'password', 'passcode', 'hardcode'
PASSCODE_DEVICE = getattr(settings, 'MULTAUTH_PASSCODE_DEVICE', None);
SECRETS = tuple(getattr(settings, 'MULTAUTH_SECRETS', (
    'password', 'passcode', 'hardcode',
)));


class AbstractUser(AbstractBaseUser, UserDevicesMixin, PermissionsMixin):

    first_name = models.CharField(_('First name'), max_length=30, null=True, blank=True)
    last_name = models.CharField(_('Last name'), max_length=150, null=True, blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    REQUIRED_FIELDS = [] # TODO: think about it
    SECRETS = SECRETS

    # TODO: automatically create and update Device information when
    # corresponding user fields are affected

    class Meta:
        abstract = True
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return '{0} ({1})'.format(
            self.get_full_name() or 'Noname',
            ', '.join([str(getattr(self, i)) for i in self.IDENTIFIERS if getattr(self, i)]) or '-', # experimental
        ).strip()

    def get_full_name(self):
        return '{0} {1}'.format(self.first_name or '', self.last_name or '').strip()

    def get_short_name(self):
        return self.first_name

    def verify(self, request=None):
        super().verify(request)

    # TODO: how about to make device required
    def set_passcode(self, device=None):
        # TODO: apply PASSCODE_DEVICE 

        # reserved
        # if not device or not device.is_interactive:
        #     raise self.__class__.DoesNotExist('No interactive device found')

        return device.generate_challenge()

    def check_passcode(self, passcode, device=None):
        # don't mess this "token" with authorization tokens
        if device:
            return device.verify_token(passcode)
        else:
            # TODO: what's this???
            return bool(match_token(self, passcode))

    # TODO: how about to make device required
    def set_hardcode(self, raw_hardcode, device=None):
        if not user.pk:
            raise self.__class__.DoesNotExist('User should be saved, before setting hardcode')

        if not device:
            devices = [x for x in self.get_devices() if hasattr(x, 'hardcode')]
            device = devices[0] if devices else None

        if not device or not device.has_hardcode:
            raise self.__class__.DoesNotExist('No device having hardcode found')

        device.set_hardcode(raw_hardcode)

    def check_hardcode(self, raw_hardcode, device=None):
        if not device:
            devices = [x for x in self.get_devices() if hasattr(x, 'hardcode')]
            device = devices[0] if devices else None

        if not device or not device.has_hardcode:
            raise self.__class__.DoesNotExist('No device having hardcode found')

        return device.check_hardcode(raw_hardcode)


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
