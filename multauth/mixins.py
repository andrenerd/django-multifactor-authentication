from django.conf import settings
from .decorators import (
    is_authenticated,
    is_admin,
    # is_custom_user, # EXAMPLE
)


MULTAUTH_DEVICES = getattr(settings, 'MULTAUTH_DEVICES', {})

devices_mixin = lambda devices: tuple([d.USER_MIXIN for d in devices]) # don't touch

def devices_mixin_verify(self, request=None):
  for base in DevicesMixin.__bases__:
    base.verify(self, request)

DevicesMixin = type(
    'DevicesMixin',
    devices_mixin(list(MULTAUTH_DEVICES.values())),
    {'verify': devices_mixin_verify}
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
