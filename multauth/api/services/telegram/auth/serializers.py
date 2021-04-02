from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, serializers
from multauth.services import TelegramService


__all__ = (
    'SignupVerificationTelegramSerializer',
    'SigninPasscodeTelegramSerializer',
)


class SignupVerificationTelegramSerializer(serializers.Serializer):
    token = serializers.CharField() # aka passcode

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        if user.check_telegram_passcode(data.get('token')):
            service = user.get_telegram_service()
            service.confirmed = True
            service.save()
            # reserved # user.is_active = True
            # reserved # user.save()

        else:
            raise serializers.ValidationError(_('Confirmation code is invalid or expired'))

        return super().validate(data)


class SigninPasscodeTelegramSerializer(serializers.Serializer):
    telegram = serializers.CharField()

    def validate(self, data):
        telegram = data.get('telegram')

        if telegram:
            try:
                service = TelegramService.objects.get(telegram=telegram)
                service.set_passcode()
            except TelegramService.DoesNotExist:
                pass

        return super().validate(data)
