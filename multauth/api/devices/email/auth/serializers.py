from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import exceptions, serializers


__all__ = (
    'SignupVerificationPhoneSerializer',
    'SignupVerificationEmailSerializer',
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


class SignupVerificationUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            'phone', 'email',
            'is_phone_confirmed', 'is_email_confirmed',
            'is_active',
        )


# based on rest_framework.authtoken.serializers.SigninSerializer
class SigninSerializer(serializers.Serializer):
    phone = serializers.CharField(required=False)
    passcode = serializers.CharField(required=False, style={'input_type': 'password'})

    email = serializers.CharField(required=False)
    password = serializers.CharField(required=False, style={'input_type': 'password'})

    token = serializers.CharField(required=False) # aka one-time-passcode

    def validate(self, data):
        """
        Authenticate user by one of the credential pairs
        - phone/passcode/token (one-time-password) (yes, by three params)
        - email/password
        - email/token
        """

        if not (
            (data.get('phone') and data.get('passcode')) or # ignore token
            (data.get('email') and data.get('password'))
        ):
            msg = _('Must include "phone/passcode" or "email/password".')
            raise exceptions.ValidationError(msg)

        user = authenticate(**data)

        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        data['user'] = user
        return super().validate(data)
