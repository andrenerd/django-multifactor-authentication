from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import exceptions, serializers


__all__ = (
    'UserSerializer',
)


class UserSerializer(serializers.ModelSerializer):
    """
    For read (GET) requests only
    """
    # custom_user = _UserCustomUserSerializer(required=False) # sample

    phone = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    # RESERVED # is_phone_pushcoded = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'first_name', 'last_name',
            'phone', 'email',
            'date_joined',
            'last_login',
            'groups',
            'is_phone_verified',
            'is_email_verified',
            # RESERVED # 'is_phone_pushcoded',

            # 'custom_user', # sample
        )
        read_only_fields = (
            'date_joined',
            'last_login',
            'is_phone_verified',
            'is_email_verified',
            # RESERVED # 'is_phone_pushcoded',
            'groups',
        )

    # RESERVED
    # def get_is_phone_pushcoded(self, obj):
    #     if obj.phone and obj.is_phone_verified:
    #         try:
    #             device = obj.get_phone_device()
    #             return bool(device.pushcode)
    #         except:
    #             return False
    #     else:
    #         return False

    def update(self, instance, validated_data):
        user = instance

        # update credential fields with initial values only
        if user.phone:
            validated_data.pop('phone', None)

        if user.email:
            validated_data.pop('email', None)

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
