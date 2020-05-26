from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, parsers, mixins, views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

# from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body

from .. import PhoneDevice

# from ..permissions import IsCustomUser
from . import serializers


class MeView(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer

    @swagger_auto_schema(
        operation_description='Get user details',
        responses={
            200: serializers.UserSerializer,
        }
    )
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description='''
            Set user details.
            Credential fields, such as phone and email
            could be update with initial values (ie once) only.
        ''',
        request_body=serializers.UserSerializer,
        responses={
            200: serializers.UserSerializer,
        }
    )
    @transaction.atomic
    def post(self, request):
        data = request.data
        user = request.user

        serializer = serializers.UserSerializer(user,
            data=data, partial=True) # context={'request': request}

        serializer.is_valid(raise_exception=True)

        phone_old = user.phone
        email_old = user.email

        user = serializer.save()

        if user.phone is not phone_old:
            user.verify_phone(request)
        if user.email is not email_old:
            user.verify_email(request)

        serializer = self.serializer_class(user)
        return Response(serializer.data)


class MePasscodeView(views.APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description='Set user passcode',
        request_body=serializers.UserPasscodeSerializer,
    )
    def post(self, request):
        serializer = serializers.UserPasscodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.set_passcode(serializer.validated_data['passcode'])
        request.user.save()

        return Response(status=status.HTTP_200_OK)


# TODO: update later... drop passwords comparison
class MePasswordView(views.APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description='Set user password',
        request_body=serializers.UserPasswordSerializer,
    )
    def post(self, request):
        serializer = serializers.UserPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['password'])
        request.user.save()

        return Response(status=status.HTTP_200_OK)


class MePushcodeView(views.APIView):
    """ Set token (aka pushcode) for push notifications """
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description='Set push notification code, aka token',
        request_body=serializers.UserPushcodeSerializer,
    )
    def post(self, request):
        serializer = serializers.UserPushcodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = request.user
            device = PhoneDevice.objects.get(phone=user.phone)
            device.pushcode = serializer.validated_data['pushcode'];
            device.save()

            return Response(status=status.HTTP_200_OK)

        except PhoneDevice.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
