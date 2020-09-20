from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, serializers
from multauth.devices import PhoneDevice


__all__ = (
    'SignupVerificationPhoneSerializer',
    'SigninPasscodePhoneSerializer',
)


class SignupVerificationPhoneSerializer(serializers.Serializer):
    token = serializers.CharField() # aka one-time-passcode

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        if user.verify_phone_token(data.get('token')):
            device = user.get_phone_device()
            device.confirmed = True
            device.save()
            # reserved # user.is_active = True
            # reserved # user.save()

        else:
            raise serializers.ValidationError(_('Confirmation code is invalid or expired'))

        return super().validate(data)


class SigninPasscodePhoneSerializer(serializers.Serializer):
    phone = serializers.CharField()
    hardcode = serializers.CharField(required=False) # mostly required

    def validate(self, data):
        phone = data.get('phone')
        hardcode = data.get('hardcode')

        if phone:
            try:
                device = PhoneDevice.objects.get(phone=phone)
                if not hardcode or device.check_hardcode(hardcode):
                    device.generate_challenge()
            except PhoneDevice.DoesNotExist:
                pass

        return super().validate(data)
