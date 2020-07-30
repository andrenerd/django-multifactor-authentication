from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, serializers


__all__ = (
    'UserPasswordSerializer',
)


class UserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    # password_old = serializers.CharField()
