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

        serializer = serializers.UserSerializer(user,
            data=data, partial=True, context={'request': request})

        serializer.is_valid(raise_exception=True)

        serializer = self.serializer_class(user)
        return Response(serializer.data)
