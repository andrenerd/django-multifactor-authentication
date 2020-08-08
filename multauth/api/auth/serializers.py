from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import exceptions, serializers

UserModel = get_user_model()
IDENTIFIERS = list(UserModel.IDENTIFIERS)
SECRETS = list(UserModel.SECRETS)
SECRETS_WITHOUT_PASSCODE = [x for x in SECRETS if x != 'passcode']


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
    hardcode = serializers.CharField(required=False)

    class Meta:
        model = UserModel
        fields = tuple([]
            + ['first_name', 'last_name']
            + IDENTIFIERS
            + SECRETS_WITHOUT_PASSCODE
        )

        # experimental
        extra_kwargs = dict([]
            + [(x, {'required': False}) for x in IDENTIFIERS] # 'validators': None
            + [(x, {'required': False}) for x in SECRETS_WITHOUT_PASSCODE]
        )

    def validate(self, data):
        data = super(SignupSerializer, self).validate(data)
        model = self.Meta.model

        # check identifiers
        data_identifiers = [x for x in data if x in IDENTIFIERS and data.get(x, None)]
        if not data_identifiers:
            msg = _('Invalid user credentials. No valid identifier found')
            raise exceptions.ValidationError(msg)

        # create user and related devices
        user_data = dict([(x, data[x]) for x in data.keys() if x not in ['hardcode']])
        user = model.objects.create_user(**user_data)

        # save extra devices fields
        if data.get('hardcode', None):
            for device in user.get_devices():
                if device.has_hardcode:
                    device.set_hardcode(data['hardcode'])

        data['user'] = user
        return data


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


signin_serializer_fields = dict([
    [x, serializers.ModelField(model_field=UserModel()._meta.get_field(x), required=False)]
        for x in (IDENTIFIERS + SECRETS) if hasattr(UserModel, x)
])


def signin_serializer_validate(self, data):
    data = super(SigninSerializer, self).validate(data)
    # model = self.Meta.model

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
    return data


SigninSerializer = type(
    'SigninSerializer',
    (serializers.Serializer,),
    {
        # reserved # '__module__': 'multauth.api.auth',
        'validate': signin_serializer_validate,
        'hardcode': serializers.CharField(required=False),
        'passcode': serializers.CharField(required=False),
        **signin_serializer_fields,
    }
)
