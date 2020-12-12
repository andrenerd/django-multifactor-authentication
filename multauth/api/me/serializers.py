from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import exceptions, serializers

UserModel = get_user_model()
IDENTIFIERS = list(UserModel.IDENTIFIERS)


__all__ = (
    'UserSerializer',
    'UserPasswordSerializer',
    'UserPasscodeSerializer',
)


class UserSerializer(serializers.ModelSerializer):
    # custom_user = _UserCustomUserSerializer(required=False) # sample

    class Meta:
        model = UserModel
        fields = tuple([]
            + ['id', 'first_name', 'last_name']
            + ['date_joined', 'last_login', 'groups']
            + IDENTIFIERS
            + ['is_' + x + '_confirmed' for x in IDENTIFIERS if hasattr(UserModel, 'is_' + x + '_confirmed')] # ex. ['is_email_confirmed']
        )

        read_only_fields = (
            'id', 'date_joined', 'last_login', 'groups',
        )

    def update(self, instance, validated_data):
        user = instance

        # sample
        # if user.is_custom_user:
        #     data_custom_user = validated_data.pop('custom_user', {})
        #     custom_user = user.custom_user

        #     if data_custom_user:
        #         serializer_custom_user = _UserCustomUserSerializer(
        #             custom_user, data=data_custom_user, partial=True)
        #         serializer_custom_user.is_valid(raise_exception=True)
        #         serializer_custom_user.save()

        return super().update(user, validated_data)


class UserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    # password_old = serializers.CharField()


class UserPasscodeSerializer(serializers.Serializer):
    passcode = serializers.CharField()
    # passcode_old = serializers.CharField()
