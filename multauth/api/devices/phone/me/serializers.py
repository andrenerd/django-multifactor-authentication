from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, serializers


__all__ = (
    'UserPhonePushcodeSerializer',
)


class UserPhonePushcodeSerializer(serializers.Serializer):
    pushcode = serializers.CharField()
