from importlib import import_module

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django_otp import devices_for_user

from .devices import UsernameDevice, EmailDevice, PhoneDevice
from .decorators import (
    is_authenticated,
    is_admin,
    # is_custom_user, # EXAMPLE
)


DEVICES = tuple(getattr(settings, 'MULTAUTH_DEVICES', [
    UsernameDevice,
    EmailDevice,
    PhoneDevice,
]));


mixin_classes = tuple(
    getattr(import_module(d.__module__), d.USER_MIXIN) for d in DEVICES
)

if not mixin_classes:
    msg = _('At least one Device should be added (see MULTAUTH_DEVICES settings)')
    raise ValueError(msg)

mixin_identifiers = tuple(
    c.IDENTIFIER_FIELD for c in DEVICES if hasattr(c, 'IDENTIFIER_FIELD')
)

if not mixin_identifiers:
    msg = _('At least one identifier should be declared (see Device.IDENTIFIER_FIELD attribute)')
    raise ValueError(msg)

mixin_classes_username_fields = tuple(
    c.USERNAME_FIELD for c in mixin_classes if hasattr(c, 'USERNAME_FIELD')
)

mixin_username_field = (
    mixin_classes_username_fields[0] if mixin_classes_username_fields else mixin_identifiers[0]
)

mixin_meta_options = {
    'abstract': True,
    'unique_together': (mixin_identifiers,)
    # reserved # 'index_together': ...all possible combinations of two/three identifiers
    # reserved # 'constraints': ... probably
}

@classmethod
def mixin_get_device_classes(cls):
    return list(DEVICES)

@classmethod
def mixin_get_device_class_by_identifier(cls, identifier):
    if identifier not in mixin_identifiers:
        return None

    return DEVICES[mixin_identifiers.index(identifier)]

# TODO: add similar "pre_save" handler to update devices on identifiers updates
@classmethod
def mixin_post_save(cls, sender, instance, created, *args, **kwargs):
    """
    Create devices for created user
    """
    if not created:
        return

    user = instance
    identifiers = [x for x in instance.IDENTIFIERS if getattr(instance, x, None)]

    for identifier in identifiers:
        device_class = instance.get_device_class_by_identifier(identifier)

        d = device_class.objects.create(
            user=user,
            **{identifier: getattr(user, identifier)}
        )


def mixin_get_devices(self, confirmed=None):
    # to think: can be sorted by order in the settings
    return devices_for_user(self, confirmed)


UserDevicesMixin = type(
    'UserDevicesMixin',
    mixin_classes,
    {
        '__module__': 'multauth',
        'Meta': type('Meta', (object,), mixin_meta_options),

        'USERNAME_FIELD': mixin_username_field,
        'IDENTIFIERS': tuple(set(list(mixin_identifiers) + [mixin_username_field])), # drop duplicates

        '_post_save': mixin_post_save,
        'get_device_classes': mixin_get_device_classes,
        'get_device_class_by_identifier': mixin_get_device_class_by_identifier,
        'get_devices': mixin_get_devices,
    }
)

post_save.connect(UserDevicesMixin._post_save, sender=settings.AUTH_USER_MODEL)


class IsAuthenticatedMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(IsAuthenticatedMixin, cls).as_view(**initkwargs)
        return is_authenticated(view)


class IsAdminMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(IsAdminMixin, cls).as_view(**initkwargs)
        return is_admin(view)


# EXAMPLE
# class IsCustomUserMixin(object):
#     @classmethod
#     def as_view(cls, **initkwargs):
#         view = super(IsCustomUserMixin, cls).as_view(**initkwargs)
#         return is_custom_user(view)
