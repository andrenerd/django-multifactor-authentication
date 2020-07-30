from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, parsers, views, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# from ..permissions import IsCustomUser # EXAMPLE
from .. import TokenInactiveAuthentication
from .. import auth_serializers
from . import serializers


class SignupVerificationPhoneView(views.APIView):
    authentication_classes = (TokenInactiveAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.SignupVerificationPhoneSerializer

    # @swagger_auto_schema(
    #     operation_description='User phone verification',
    #     request_body=auth_serializers.SignupVerificationPhoneSerializer,
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
