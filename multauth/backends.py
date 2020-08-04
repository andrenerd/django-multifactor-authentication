from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.backends import ModelBackend as _ModelBackend
from django.conf import settings

UserModel = get_user_model()


FLOWS = tuple(getattr(settings, 'MULTAUTH_FLOWS', (
    ('username', 'password'),
    ('email', 'password'),
)));

FLOWS = FLOWS if type(FLOWS[0]) is tuple else tuple([FLOWS])

# TODO: validate flows here


class ModelBackend(_ModelBackend):

    FLOWS = FLOWS

    def _get_identifier(self, data):
        for identifier in UserModel.IDENTIFIERS:
            if identifier in data:
                return identifier

        return None

    def _get_flows(self, identifier):
        return [flow for flow in self.FLOWS if identifier in flow] or None

    def check_secrets(self, user, secrets, data):
        for secret in secrets:
            check_secret = getattr(self, 'check_' + secret, None)

            if not check_secret:
                return False

            if not secret in data:
                return False

            if not check_secret(user, data.get(secret)):
                return False

        return True

    # experimental
    def check_password(self, user, raw_password):
        return user.check_password(raw_password)

    # experimental
    def check_passcode(self, user, raw_passcode):
        return user.check_passcode(raw_passcode)

    # experimental
    def check_hardcode(self, user, raw_hardcode):
        return user.check_hardcode(raw_hardcode)

    def authenticate(self, request, **kwargs):
        identifier = self._get_identifier(kwargs)
        flows = self._get_flows(identifier)

        if identifier is None or flows is None:
            return

        try:
            user = UserModel._default_manager.get(**{identifier: kwargs.get(identifier)})
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(None)
        else:
            if self.user_can_authenticate(user):
                for flow in flows:
                    flow_secrets = [x for x in flow if x in UserModel.SECRETS]

                    if self.check_secrets(user, flow_secrets, kwargs):
                        return user
