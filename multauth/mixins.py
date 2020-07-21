from importlib import import_module

from django.conf import settings
from django.db import models

from .devices import EmailDevice, PhoneDevice
from .decorators import (
    is_authenticated,
    is_admin,
    # is_custom_user, # EXAMPLE
)


MULTAUTH_DEVICES = tuple(getattr(settings, 'MULTAUTH_DEVICES', [
    EmailDevice,
    PhoneDevice,
]));

if not MULTAUTH_DEVICES:
    raise ValidationError('At least one Device should be added (see MULTAUTH_DEVICES settings)')


mixin_classes = tuple(
    getattr(import_module(d.__module__), d.USER_MIXIN) for d in MULTAUTH_DEVICES
)

mixin_devices = tuple(
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
        mixin_devices[i].upper() + '_SECRET_FIELD_REQUIRED',
        getattr(x, 'SECRET_FIELD_REQUIRED', False),
    ] for (i, x) in enumerate(mixin_classes) # experimental
])


UserDevicesMixin = type(
    'UserDevicesMixin',
    mixin_classes,
    {
        '__module__': 'multauth',
        'Meta': type('Meta', (object,), {'abstract': True}),

        'USERNAME_FIELD': mixin_identifiers[0], # experimental
        'DENTIFIER_FIELD': mixin_identifiers, # experimental # just to override mixed value
        'SECRET_FIELD': mixin_secrets, # experimental # just to override mixed value
        'SECRET_FIELD_REQUIRED': None, # experimental # just to override mixed value

        '_devices': mixin_devices,
        '_identifiers': mixin_identifiers,
        '_secrets': mixin_secrets, # experimental
        '_credentials': mixin_credentials, # experimental

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
