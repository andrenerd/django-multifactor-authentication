import qrcode
import qrcode.image.svg
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse

from rest_framework import exceptions, parsers, views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from multauth.devices import AuthenticatorDevice
# from ..permissions import IsCustomUser
from . import serializers


class MeAuthenticatorKeyTextView(views.APIView):
    """ Get or refresh and get secret key for authenticator as text """
    permission_classes = (IsAuthenticated,)

    # @swagger_auto_schema(
    #     operation_description='Get authenticator key',
    #     responses={
    #         200: serializers.UserAuthenticatorKeySerializer,
    #     }
    # )
    def get(self, request):
        user = request.user

        try:
            user = request.user
            device = user.get_authenticator_device()
            key = device.key_b32

        except AuthenticatorDevice.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # @swagger_auto_schema(
    #     operation_description='Set push notification code, aka token',
    #     request_body=serializers.UserAuthenticatorPushcodeSerializer,
    # )
    # def post(self, request):
    #     serializer = serializers.UserAuthenticatorPushcodeSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     try:
    #         user = request.user
    #         device = user.get_phone_device()
    #         device.pushcode = serializer.validated_data['pushcode'];
    #         device.save()

    #         return Response(status=status.HTTP_200_OK)

    #     except AuthenticatorDevice.DoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND)


class MeAuthenticatorKeyImageView(views.APIView):
    """ Get or refresh and get secret key for authenticator as qr-code """
    permission_classes = (IsAuthenticated,)

    # @swagger_auto_schema(
    #     operation_description='Get authenticator key',
    #     responses={
    #         200: serializers.UserAuthenticatorKeySerializer,
    #     }
    # )
    def get(self, request):
        user = request.user

        try:
            user = request.user
            device = user.get_authenticator_device()
            uri = device.key_uri

            img = qrcode.make(uri, image_factory=qrcode.image.svg.SvgImage)
            response = HttpResponse(content_type='image/svg+xml; charset=utf-8')
            img.save(response)
            return response

        except AuthenticatorDevice.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # @swagger_auto_schema(
    #     operation_description='Set push notification code, aka token',
    #     request_body=serializers.UserAuthenticatorPushcodeSerializer,
    # )
    # def post(self, request):
    #     serializer = serializers.UserAuthenticatorPushcodeSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     try:
    #         user = request.user
    #         device = user.get_phone_device()
    #         device.pushcode = serializer.validated_data['pushcode'];
    #         device.save()

    #         return Response(status=status.HTTP_200_OK)

    #     except AuthenticatorDevice.DoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND)
