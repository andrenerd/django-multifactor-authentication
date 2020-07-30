from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, parsers, views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from ..permissions import IsCustomUser
from .. import me_serializers
from . import serializers


# TODO: update later... drop passwords comparison
class MePasswordView(views.APIView):
    permission_classes = (IsAuthenticated,)

    # @swagger_auto_schema(
    #     operation_description='Set user password',
    #     request_body=serializers.UserPasswordSerializer,
    # )
    def post(self, request):
        serializer = serializers.UserPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['password'])
        request.user.save()

        return Response(status=status.HTTP_200_OK)
