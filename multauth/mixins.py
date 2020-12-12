from importlib import import_module

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.utils.module_loading import import_string
from django.conf import settings
from django_otp import devices_for_user

from .services import UsernameService, EmailService, PhoneService
from .decorators import (
    is_authenticated,
    is_admin,
    # is_custom_user, # EXAMPLE
)


SERVICES = tuple(import_string(d) for d in tuple(getattr(settings, 'MULTAUTH_SERVICES', [
    'multauth.services.UsernameService',
    'multauth.services.EmailService',
    'multauth.services.PhoneService',
])));

mixin_classes = tuple(
    getattr(import_module(d.__module__), d.USER_MIXIN) for d in SERVICES
)

if not mixin_classes:
    msg = _('At least one Service should be added (see MULTAUTH_SERVICES settings)')
    raise ValueError(msg)

mixin_identifiers = tuple(
    c.IDENTIFIER_FIELD for c in SERVICES if getattr(c, 'IDENTIFIER_FIELD', None)
)

if not mixin_identifiers:
    msg = _('At least one identifier should be declared (see Service.IDENTIFIER_FIELD attribute)')
    raise ValueError(msg)

mixin_classes_username_fields = tuple(
    c.USERNAME_FIELD for c in mixin_classes if getattr(c, 'USERNAME_FIELD', None)
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
def mixin_get_service_classes(cls):
    return list(SERVICES)

@classmethod
def mixin_get_service_class_by_identifier(cls, identifier):
    if identifier not in mixin_identifiers:
        return None

    return SERVICES[mixin_identifiers.index(identifier)]

# todo: refactor, should be called for "updated" identifiers only
@classmethod
def mixin_post_save(cls, sender, instance, *args, **kwargs):
    """
    Create or update services with identifiers
    """
    user = instance
    identifiers = [x for x in instance.IDENTIFIERS if getattr(instance, x, None)]

    for identifier in identifiers:
        service_class = instance.get_service_class_by_identifier(identifier)

        if service_class._meta.abstract:
            continue

        values = {'user': user, identifier: getattr(user, identifier)}

        try:
            d = service_class.objects.get(**values)
        except service_class.DoesNotExist:
            d = None

        if not d:
            service_class.objects.create(**values)


@classmethod
def mixin_post_create(cls, sender, instance, created, *args, **kwargs):
    """
    Create or update services without indetifiers
    """
    if not created:
        return

    user = instance
    service_classes = tuple(
        c for c in SERVICES if not getattr(c, 'IDENTIFIER_FIELD', None)
    )

    for service_class in service_classes:
        values = {'user': user}

        try:
            d = service_class.objects.get(**values)
        except service_class.DoesNotExist:
            d = None

        if not d:
            service_class.objects.create(**values)


def mixin_get_services(self, confirmed=None):
    # to think: can be sorted by order in the settings
    return devices_for_user(self, confirmed)


UserServicesMixin = type(
    'UserServicesMixin',
    mixin_classes,
    {
        '__module__': 'multauth',
        'Meta': type('Meta', (object,), mixin_meta_options),

        'USERNAME_FIELD': mixin_username_field,
        'IDENTIFIERS': tuple(set(list(mixin_identifiers) + [mixin_username_field])), # drop duplicates

        '_post_save': mixin_post_save,
        '_post_create': mixin_post_create,
        'get_service_classes': mixin_get_service_classes,
        'get_service_class_by_identifier': mixin_get_service_class_by_identifier,
        'get_services': mixin_get_services,
    }
)

post_save.connect(UserServicesMixin._post_save, sender=settings.AUTH_USER_MODEL)
post_save.connect(UserServicesMixin._post_create, sender=settings.AUTH_USER_MODEL)


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
