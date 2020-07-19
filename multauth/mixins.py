from importlib import import_module

from django.conf import settings
from django.db import models

from .devices import EmailDevice, PhoneDevice
from .decorators import (
    is_authenticated,
    is_admin,
    # is_custom_user, # EXAMPLE
)


MULTAUTH_DEVICES = list(getattr(settings, 'MULTAUTH_DEVICES', [
    EmailDevice,
    PhoneDevice,
]));


mixin_classes = tuple(
    getattr(import_module(d.__module__), d.USER_MIXIN) for d in MULTAUTH_DEVICES
)

mixin_modules = tuple(
    c.__module__.split('.')[-1] for c in mixin_classes
)

mixin_identifiers = tuple(
    c.IDENTIFIER_FIELD for c in mixin_classes
)

mixin_secrets = tuple(
    c.SECRET_FIELD for c in mixin_classes # experimental
)

mixin_credentials = tuple(
    (x, mixin_secrets[i]) for (i, x) in enumerate(mixin_identifiers) # experimental
)

mixin_settings = dict([
    [
        mixin_modules[i].upper() + '_SECRET_FIELD_REQUIRED',
        getattr(x, 'SECRET_FIELD_REQUIRED', False),
    ] for (i, x) in enumerate(mixin_classes) # experimental
])


# experimental # dirty
def clean_mixin_classes(mixin_classes):
    for x in mixin_classes:
        delattr(x, 'IDENTIFIER_FIELD')
        delattr(x, 'SECRET_FIELD')
        delattr(x, 'SECRET_FIELD_REQUIRED')

    return mixin_classes


def devices_mixin_verify(self, request=None):
    for base in UserDevicesMixin.__bases__:
        base.verify(self, request)


UserDevicesMixin = type(
    'UserDevicesMixin',
    clean_mixin_classes(mixin_classes),
    {
        '__module__': 'multauth',
        'Meta': type('Meta', (object,), {'abstract': True}),

        '_devices': mixin_modules,
        '_identifiers': mixin_identifiers,
        '_secrets': mixin_secrets, # experimental
        '_credentials': mixin_credentials, # experimental

        'verify': devices_mixin_verify,

        **mixin_settings,
    }
)


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
