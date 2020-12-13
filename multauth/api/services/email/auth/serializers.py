from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import exceptions, serializers
from multauth.services import EmailService


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

        if user.check_email_passcode(data.get('token')):
            service = user.get_email_service()
            service.confirmed = True
            service.save()
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
                service = user.get_email_service()
                service.confirmed = True
                service.save()
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
                service = EmailService.objects.get(email=email)
                service.generate_challenge()
            except EmailService.DoesNotExist:
                pass

        return super().validate(data)
