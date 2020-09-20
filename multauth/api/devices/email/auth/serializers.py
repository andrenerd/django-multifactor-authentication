from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import exceptions, serializers
from multauth.devices import EmailDevice


__all__ = (
    'SignupVerificationEmailSerializer',
    'SignupVerificationEmailKeySerializer',
    'SigninPasscodeEmailSerializer',
)


class SignupVerificationEmailSerializer(serializers.Serializer):
    token = serializers.CharField() # aka one-time-passcode

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        if user.verify_email_token(data.get('token')):
            device = user.get_email_device()
            device.confirmed = True
            device.save()
            # reserved # user.is_active = True
            # reserved # user.save()

        else:
            msg = _('Confirmation code is invalid or expired')
            raise exceptions.ValidationError(msg)

        return super().validate(data)


class SignupVerificationEmailKeySerializer(serializers.Serializer):
    key = serializers.CharField(required=True)

    def validate(self, data):
        # TODO: prevent double call for the function/endpoint
        user = get_user_model().verify_email_key(data['key'])

        if user:
            if not user.is_email_confirmed:
                device = user.get_email_device()
                device.confirmed = True
                device.save()
                # reserved # user.is_active = True
                # reserved # user.save()

            data['user'] = user

        else:
            msg = _('Confirmation code is invalid or expired')
            raise exceptions.ValidationError(msg)

        return super().validate(data)


# experimental. weak.
class SigninPasscodeEmailSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate(self, data):
        email = data.get('email')

        if email:
            try:
                device = EmailDevice.objects.get(email=email)
                device.generate_challenge()
            except EmailDevice.DoesNotExist:
                pass

        return super().validate(data)
