from functools import reduce

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.hashers import check_password, make_password
# from django.contrib.auth.validators import UnicodeUsernameValidator

from .managers import UserManager
from .mixins import UserDevicesMixin


class AbstractUser(UserDevicesMixin, AbstractBaseUser, PermissionsMixin):

    # username_validator = UnicodeUsernameValidator()

    # TODO: move to UsernameDevice
    # username = models.CharField(_('username'), max_length=150, unique=True, # editable=False
    #     help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    #     validators=[username_validator],
    #     error_messages={
    #         'unique': _("A user with that username already exists."),
    #     },
    # )

    first_name = models.CharField(_('First name'), max_length=30, null=True, blank=True)
    last_name = models.CharField(_('Last name'), max_length=150, null=True, blank=True)

    objects = UserManager()

    REQUIRED_FIELDS = [] # TODO: think about it

    class Meta:
        abstract = True
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return '{0} ({1})'.format(
            self.get_full_name() or 'Noname',
            ', '.join([getattr(self, i) for i in self._identifiers if getattr(self, i)]) or '-', # experimental
        ).strip()

    # experimental
    @classmethod
    def get_required_credentials(cls):
        attr = lambda x: '_'.join((x.upper(), 'SECRET_FIELD_REQUIRED'))

        return tuple(map(
            lambda i, x: x if getattr(cls, attr(cls._devices[i]), False) else (x[0],), # drop non required secrets
            range(cls._credentials.__len__()), cls._credentials,
        ))

    @classmethod
    def validate(cls, **fields):
        required_credentials = cls.get_required_credentials()

        # at least one "pair" of credentials should be present
        if not [
            credentials for credentials in required_credentials
                if reduce(lambda b, x: fields.get(x) and b, credentials, True)
        ]:
            msg = _('Invalid user credentials. Must include ' + ' or '.join('"' + '/'.join(x) + '"' for x in required_credentials))
            raise ValueError(msg)

    def get_full_name(self):
        return '{0} {1}'.format(self.first_name or '', self.last_name or '').strip()

    def get_short_name(self):
        return self.first_name

    def set_secrets(self, **fields):
        super().set_secrets(**fields)


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
