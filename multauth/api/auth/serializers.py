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


class SigninSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=False) # aka one-time-passcode

    class Meta:
        model = get_user_model()
        identifiers_fields = [x for x in model.IDENTIFIERS]
        secrets_fields = [x for x in model.SECRETS]

        fields = tuple(identifiers_fields + secrets_fields + [
            'token'
        ])

        extra_kwargs = dict([]
            + [(x, {'required': False, 'validators': None}) for x in identifiers_fields]
            + [(x, {'required': False}) for x in secrets_fields]
        )

    # # TODO refactor and add to validate()
    # # the requirements would be: indentifier and at "first" secret are required
    # @classmethod
    # def validate(cls, required_only=True, **fields):
    #     # TEMP
    #     return

    #     # TODO: move it to ModelBackend !
    #     # TODO: temp
    #     required_credentials = list(cls.IDENTIFIERS) + list(cls.SECRETS)
    #     # RESERVED
    #     # required_credentials = \
    #     #     cls.get_required_credentials() if required_only else cls._credentials

    #     # at least one "pair" of credentials should be present
    #     if not [
    #         credentials for credentials in required_credentials
    #             if reduce(lambda b, x: fields.get(x) and b, credentials, True)
    #     ]:
    #         msg = _('Invalid user credentials. Must include ' + ' or '.join('"' + '/'.join(x) + '"' for x in required_credentials))
    #         raise ValueError(msg)
    def validate(self, data):
        model = self.Meta.model

        try:
            model.validate(required_only=False, **data) # experimental
        except ValueError as e:
            raise exceptions.ValidationError(str(e))

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


class SignupSerializer(serializers.ModelSerializer):
    """
    For write (POST...) requests only
    """
    class Meta:
        model = get_user_model()
        credentials_fields = list(model.IDENTIFIERS) + list(model.SECRETS)

        fields = tuple(credentials_fields + [
            'first_name', 'last_name',
        ])

        extra_kwargs = dict(
            (x, {'required': False}) for x in credentials_fields
        )

    def validate(self, data):
        model = self.Meta.model

        try:
            model.validate(**data) # experimental
        except ValueError as e:
            raise exceptions.ValidationError(str(e))

        return super().validate(data)


class SignupVerificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        identifiers_fields = [x for x in model.IDENTIFIERS]

        fields = tuple(identifiers_fields + [
            # pass
        ])


class SignupVerificationUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        identifiers_fields = [x for x in model.IDENTIFIERS]
        extra_fields = [f.name for f in model._meta.get_fields() if f.name.endswith('verified')] # tricky

        fields = tuple(identifiers_fields + extra_fields + [
            'is_active',
        ])
