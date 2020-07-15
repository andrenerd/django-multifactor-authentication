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


mixin_classes = tuple([
    getattr(import_module(d.__module__), d.USER_MIXIN) for d in MULTAUTH_DEVICES
])


def devices_mixin_verify(self, request=None):
    for base in UserDevicesMixin.__bases__:
        base.verify(self, request)


def get_devices_names(self):
    return [base.__str__(self) for base in UserDevicesMixin.__bases__]


UserDevicesMixin = type(
    'UserDevicesMixin',
    mixin_classes,
    {
        '__module__': 'multauth',
        'verify': devices_mixin_verify,
        'get_devices_names': get_devices_names # experimental
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
