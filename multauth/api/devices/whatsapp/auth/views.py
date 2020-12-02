from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, parsers, views, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# from ..permissions import IsCustomUser # EXAMPLE
from .. import TokenInactiveAuthentication
from .. import auth_serializers
from . import serializers


class SignupVerificationWhatsappView(views.APIView):
    authentication_classes = (TokenInactiveAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.SignupVerificationWhatsappSerializer

    # @swagger_auto_schema(
    #     operation_description='User WhatsApp verification',
    #     request_body=auth_serializers.SignupVerificationWhatsappSerializer,
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


class SigninPasscodeWhatsappView(views.APIView):
    # @swagger_auto_schema(
    #     operation_description='Send signin passcode to device:whatsapp',
    #     request_body=serializers.SigninPasscodeWhatsappSerializer,
    # )
    def post(self, request):
        serializer = serializers.SigninPasscodeWhatsappSerializer(data=request.data)
        serializer.is_valid(raise_exception=False) # no exceptions here
        return Response(status=status.HTTP_200_OK)
