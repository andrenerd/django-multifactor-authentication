from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, parsers, views, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

# from ..permissions import IsCustomUser # EXAMPLE
from ..authentication import TokenInactiveAuthentication
from . import serializers


class SigninView(views.APIView):
    authentication_classes = ()
    throttle_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = serializers.SigninSerializer
    parser_classes = (
        parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,
    )

    # @swagger_auto_schema(
    #     operation_description='Signin user',
    #     request_body=serializers.SigninSerializer,
    #     responses={
    #         200: serializers.TokenSerializer,
    #         400: 'Unable to login with provided credentials',
    #     }
    # )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # check if user is authenticated
        if not user or not user.is_authenticated:
            raise exceptions.NotAuthenticated()

        # lets (re)create token
        token, _ = Token.objects.get_or_create(user=user)

        serializer = serializers.TokenSerializer({
            'token': token.key
            # 'expired_datetime': 'Not implemented...'
        })

        return Response(serializer.data)


class SignupView(views.APIView):
    authentication_classes = ()
    throttle_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = serializers.SignupSerializer

    # @swagger_auto_schema(
    #     operation_description='Signup user',
    #     request_body=serializers.SignupSerializer,
    #     responses={
    #         201: serializers.TokenSerializer,
    #         400: 'Error...',
    #         409: 'Conflict: duplicate user...',
    #     }
    # )
    @transaction.atomic
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

        # TODO: refactor
        # send confirmation code if user exists
        except Exception as e:
            if hasattr(e, 'get_full_details'):
                errors = e.get_full_details().get('phone')

                if errors:
                    code = errors.pop()['code']

                    if code == 'unique':
                        user = get_user_model().objects.get(phone=data.get('phone'))

                        if user.check_passcode(data.get('passcode')):
                            user.verify_phone(request)

            raise e

        # create user
        user = get_user_model().objects.create_user(**validated_data)

        # EXAMPLE
        # TODO: move to connectors
        # create custom user
        # custom_user = CustomUser.objects.create(
        #     user = user,
        # )
        #
        # user.groups_add(user.GROUP_CUSTOM_USER)

        user.verify(request)

        # let's (re)create token
        token, _ = Token.objects.get_or_create(user=user)

        serializer = serializers.TokenSerializer({
            'token': token.key
            # 'expired_datetime': 'Not implemented...'
        })

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SignupVerificationView(views.APIView):
    authentication_classes = (TokenInactiveAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.SignupVerificationSerializer

    # @swagger_auto_schema(
    #     operation_description='Repeat verification',
    #     request_body=serializers.SignupVerificationSerializer,
    #     responses={
    #         200: serializers.SignupVerificationUserSerializer,
    #     }
    # )
    @transaction.atomic
    def post(self, request):
        user = request.user

        user.verify(request)

        serializer = serializers.SignupVerificationUserSerializer(user)
        return Response({})
