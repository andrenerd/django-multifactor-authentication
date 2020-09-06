from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django.conf import settings

from rest_framework import exceptions, parsers, views, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# from ..permissions import IsCustomUser # EXAMPLE
from .. import TokenInactiveAuthentication
from .. import auth_serializers
from . import serializers


class SignupVerificationEmailView(views.APIView):
    authentication_classes = (TokenInactiveAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.SignupVerificationEmailSerializer

    # @swagger_auto_schema(
    #     operation_description='User email verification',
    #     request_body=serializers.SignupVerificationEmailSerializer,
    #     responses={
    #         200: auth_serializers.SignupVerificationUserSerializer,
    #     }
    # )
    @transaction.atomic
    def post(self, request):
        user = request.user

        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        serializer = auth_serializers.SignupVerificationUserSerializer(user)
        return Response(serializer.data)


class SignupVerificationEmailKeyView(views.APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = serializers.SignupVerificationEmailKeySerializer

    # @swagger_auto_schema(
    #     operation_description='User email (by key) verification',
    #     responses={
    #         200: auth_serializers.TokenSerializer,
    #     }
    # )
    @transaction.atomic
    def get(self, request, key=None):
        serializer = self.serializer_class(data={'key': key})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        MULTAUTH_EMAIL_REDIRECT = getattr(settings, 'MULTAUTH_EMAIL_REDIRECT', '/')
        return redirect(MULTAUTH_EMAIL_REDIRECT, user=user)
