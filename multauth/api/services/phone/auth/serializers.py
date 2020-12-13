from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, serializers
from multauth.services import PhoneService


__all__ = (
    'SignupVerificationPhoneSerializer',
    'SigninPasscodePhoneSerializer',
)


class SignupVerificationPhoneSerializer(serializers.Serializer):
    token = serializers.CharField() # aka one-time-passcode

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        if user.check_phone_passcode(data.get('token')):
            service = user.get_phone_service()
            service.confirmed = True
            service.save()
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
                service = PhoneService.objects.get(phone=phone)
                if not hardcode or service.check_hardcode(hardcode):
                    service.generate_challenge()
            except PhoneService.DoesNotExist:
                pass

        return super().validate(data)
