from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, serializers
from multauth.devices import WhatsappDevice


__all__ = (
    'SignupVerificationWhatsappSerializer',
    'SigninPasscodeWhatsappSerializer',
)


class SignupVerificationWhatsappSerializer(serializers.Serializer):
    token = serializers.CharField() # aka one-time-passcode

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        if user.verify_whatsapp_token(data.get('token')):
            device = user.get_whatsapp_device()
            device.confirmed = True
            device.save()
            # reserved # user.is_active = True
            # reserved # user.save()

        else:
            raise serializers.ValidationError(_('Confirmation code is invalid or expired'))

        return super().validate(data)


class SigninPasscodeWhatsappSerializer(serializers.Serializer):
    whatsapp = serializers.CharField()

    def validate(self, data):
        whatsapp = data.get('whatsapp')

        if whatsapp:
            try:
                device = WhatsappDevice.objects.get(whatsapp=whatsapp)
                device.generate_challenge()
            except WhatsappDevice.DoesNotExist:
                pass

        return super().validate(data)
