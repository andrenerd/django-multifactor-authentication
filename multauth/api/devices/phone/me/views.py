from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, parsers, views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from ..permissions import IsCustomUser
from .. import me_serializers
from . import serializers


class MePasscodeView(views.APIView):
    permission_classes = (IsAuthenticated,)

    # @swagger_auto_schema(
    #     operation_description='Set user passcode',
    #     request_body=serializers.UserPasscodeSerializer,
    # )
    def post(self, request):
        serializer = serializers.UserPasscodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.set_passcode(serializer.validated_data['passcode'])
        request.user.save()

        return Response(status=status.HTTP_200_OK)


class MePushcodeView(views.APIView):
    """ Set token (aka pushcode) for push notifications """
    permission_classes = (IsAuthenticated,)

    # @swagger_auto_schema(
    #     operation_description='Set push notification code, aka token',
    #     request_body=serializers.UserPushcodeSerializer,
    # )
    def post(self, request):
        serializer = serializers.UserPushcodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = request.user
            device = user.get_phone_device()
            device.pushcode = serializer.validated_data['pushcode'];
            device.save()

            return Response(status=status.HTTP_200_OK)

        except PhoneDevice.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
