from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, serializers


__all__ = (
    'SignupVerificationPhoneSerializer',
)


class SignupVerificationPhoneSerializer(serializers.Serializer):
    token = serializers.CharField() # aka one-time-passcode

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        if user.verify_phone_token(data.get('token')):
            user.is_phone_verified = True
            user.is_active = True
            user.save()

        else:
            raise serializers.ValidationError(_('Confirmation code is invalid or expired'))

        return super().validate(data)
