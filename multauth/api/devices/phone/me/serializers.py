from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, serializers


__all__ = (
    'UserPasscodeSerializer',
    'UserPushcodeSerializer',
)


class UserPasscodeSerializer(serializers.Serializer):
    passcode = serializers.CharField()
    # passcode_old = serializers.CharField()


class UserPushcodeSerializer(serializers.Serializer):
    pushcode = serializers.CharField()
