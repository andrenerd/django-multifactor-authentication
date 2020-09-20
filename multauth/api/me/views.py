from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, parsers, views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from ..permissions import IsCustomUser
from . import serializers


class MeView(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer

    # @swagger_auto_schema(
    #     operation_description='Get user details',
    #     responses={
    #         200: serializers.UserSerializer,
    #     }
    # )
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    # @swagger_auto_schema(
    #     operation_description='''
    #         Set user details.
    #         Credential fields, such as phone and email
    #         could be update with initial values (ie once) only.
    #     ''',
    #     request_body=serializers.UserSerializer,
    #     responses={
    #         200: serializers.UserSerializer,
    #     }
    # )
    @transaction.atomic
    def post(self, request):
        data = request.data
        user = request.user

        serializer = self.serializer_class(user,
            data=data, partial=True, context={'request': request})

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        serializer = self.serializer_class(user)
        return Response(serializer.data)


class MePasswordView(views.APIView):
    permission_classes = (IsAuthenticated,)

    # @swagger_auto_schema(
    #     operation_description='Set user password',
    #     request_body=serializers.UserPasswordSerializer,
    # )
    def post(self, request):
        user = request.user
        serializer = serializers.UserPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data.get('password', None)
        if password:
            user.set_password(password)
            user.save()

        return Response(status=status.HTTP_200_OK)


# experimental
class MePasscodeView(views.APIView):
    permission_classes = (IsAuthenticated,)

    # @swagger_auto_schema(
    #     operation_description='Set or check user passcode',
    #     request_body=serializers.UserPasscodeSerializer,
    # )
    def post(self, request):
        user = request.user
        serializer = serializers.UserPasscodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        passcode = serializer.validated_data.get('passcode', None)
        if passcode:
            user.check_passcode(passcode)
        else:
            user.set_passcode()

        return Response(status=status.HTTP_200_OK)
