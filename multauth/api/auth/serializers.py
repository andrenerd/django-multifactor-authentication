from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import exceptions, serializers

UserModel = get_user_model()


__all__ = (
    'SigninSerializer',
    'SignupSerializer',
    'SignupVerificationSerializer',
    'SignupVerificationUserSerializer',
    # 'ResetSerializer', 'ResetEmailSerializer',

    'TokenSerializer',
)

IDENTIFIERS = list(UserModel.IDENTIFIERS)
SECRETS = list(UserModel.SECRETS)

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    # RESERVED # expired_datetime = serializers.DateTimeField(read_only=True) # could be timestamp


class SigninSerializer(serializers.ModelSerializer):
    hardcode = serializers.CharField(required=False)
    passcode = serializers.CharField(required=False)

    class Meta:
        model = UserModel
        fields = tuple(IDENTIFIERS + SECRETS)

        # experimental
        extra_kwargs = dict([]
            + [(x, {'required': False}) for x in IDENTIFIERS] # 'validators': None
            + [(x, {'required': False}) for x in SECRETS]
        )

    def validate(self, data):
        model = self.Meta.model

        # check identifiers
        data_identifiers = [x for x in data if x in IDENTIFIERS and data.get(x, None)]
        if not data_identifiers:
            msg = _('Invalid user credentials. No valid identifier found')
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


class SignupSerializer(serializers.ModelSerializer):
    """
    For write (POST...) requests only
    """
    hardcode = serializers.CharField(required=False)
    passcode = serializers.CharField(required=False) # useless?

    class Meta:
        model = UserModel
        fields = tuple([]
            + ['first_name', 'last_name']
            + IDENTIFIERS
            + SECRETS
        )

        # experimental
        extra_kwargs = dict([]
            + [(x, {'required': False}) for x in IDENTIFIERS] # 'validators': None
            + [(x, {'required': False}) for x in SECRETS]
        )

    def validate(self, data):
        model = self.Meta.model

        # check for one valid idntifier

        # check identifiers
        data_identifiers = [x for x in data if x in IDENTIFIERS and data.get(x, None)]
        if not data_identifiers:
            msg = _('Invalid user credentials. No valid identifier found')
            raise exceptions.ValidationError(msg)

        return super().validate(data)


class SignupVerificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = model.IDENTIFIERS


class SignupVerificationUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel

        confirmation_fields = ['is_' + x + '_confirmed' for x in model.IDENTIFIERS] # why not
        fields = tuple([]
            + list(model.IDENTIFIERS)
            + [x for x in confirmation_fields if hasattr(UserModel, x)] # only that way :/
            + ['is_active']
        )
