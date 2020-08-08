from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import exceptions, serializers

UserModel = get_user_model()
IDENTIFIERS = list(UserModel.IDENTIFIERS)


__all__ = (
    'UserSerializer',
)


class UserSerializer(serializers.ModelSerializer):
    # custom_user = _UserCustomUserSerializer(required=False) # sample

    class Meta:
        model = UserModel
        fields = tuple([]
            + ['id', 'first_name', 'last_name']
            + ['date_joined', 'last_login', 'groups']
            + IDENTIFIERS
            # todo: add "..._confirmed" field for each enabled device
        )

        read_only_fields = (
            'id', 'date_joined', 'last_login', 'groups',
        )

    def update(self, instance, validated_data, context):
        user = instance
        request = context.request

        # TODO: if identifiers updated
        # - chceck that atleast one exist
        # set as non confirmed
        # - run verification

        # update credential fields with initial values only
        if user.phone:
            validated_data.pop('phone', None)

        if user.email:
            validated_data.pop('email', None)

        phone_old = user.phone
        email_old = user.email

        user = serializer.save()

        if user.phone is not phone_old:
            user.verify_phone(request)
        if user.email is not email_old:
            user.verify_email(request)

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
