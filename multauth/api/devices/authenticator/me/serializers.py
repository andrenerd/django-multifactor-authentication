from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, serializers


__all__ = (
    'UserAuthenticatorKeySerializer',
)


class UserAuthenticatorKeySerializer(serializers.Serializer):
    key = serializers.CharField()
