from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import exceptions, serializers


__all__ = (
    'SigninSerializer',
    'SignupSerializer',
    'SignupVerificationSerializer',
    'SignupVerificationUserSerializer',
    # 'ResetSerializer', 'ResetEmailSerializer',

    'TokenSerializer',
)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    # RESERVED # expired_datetime = serializers.DateTimeField(read_only=True) # could be timestamp


class SignupSerializer(serializers.ModelSerializer):
    """
    For write (POST...) requests only
    """
    password = serializers.CharField(required=False)
    passcode = serializers.CharField(required=False)

    class Meta:
        model = get_user_model()
        fields = (
            'phone', 'email', 'password', 'passcode',
            'first_name', 'last_name',
        )

    def validate(self, data):
        if not (
            (data.get('phone') and data.get('passcode')) or # ignore token
            (data.get('email') and data.get('password'))
        ):
            msg = _('Must include "phone/passcode" or "email/password".')
            raise exceptions.ValidationError(msg)

        return super().validate(data)


class SignupVerificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            'phone', 'email',
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
            raise serializers.ValidationError('Confirmation code is invalid or expired')

        return super().validate(data)


class SignupVerificationEmailSerializer(serializers.Serializer):
    token = serializers.CharField() # aka one-time-passcode

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        if user.verify_email_token(data.get('token')):
            user.is_email_verified = True
            user.is_active = True
            user.save()

        else:
            raise serializers.ValidationError('Confirmation code is invalid or expired')

        return super().validate(data)


class SignupVerificationEmailKeySerializer(serializers.Serializer):
    key = serializers.CharField(required=True)

    def validate(self, data):
        # TODO: prevent double call for the function/endpoint
        user = get_user_model().verify_email_key(data['key'])

        if user:
            if not user.is_email_verified:
                # experimental / weak
                if not user.is_phone_verified:
                    user.is_active = True

                user.is_email_verified = True
                user.save()

            data['user'] = user

        else:
            raise serializers.ValidationError('Confirmation key is invalid or expired')

        return super().validate(data)


class SignupVerificationUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            'phone', 'email',
            'is_phone_verified', 'is_email_verified',
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
