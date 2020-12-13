from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, serializers
from multauth.services import WhatsappService


__all__ = (
    'SignupVerificationWhatsappSerializer',
    'SigninPasscodeWhatsappSerializer',
)


class SignupVerificationWhatsappSerializer(serializers.Serializer):
    token = serializers.CharField() # aka one-time-passcode

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        if user.check_whatsapp_passcode(data.get('token')):
            service = user.get_whatsapp_service()
            service.confirmed = True
            service.save()
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
                service = WhatsappService.objects.get(whatsapp=whatsapp)
                service.generate_challenge()
            except WhatsappService.DoesNotExist:
                pass

        return super().validate(data)
