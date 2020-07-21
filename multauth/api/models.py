from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from rest_framework.authtoken.models import Token


def get_token(self):
    """
    Custom helper method for User class to get user token.
    see: rest_framework.authentication.TokenAuthentication
    """
    if not hasattr(self, '_token'):
        try:
            self._token, _ = Token.objects.get_or_create(user=self)

        except IntegrityError:
            # hint: threading and concurrency makes me sick
            self._token = Token.objects.get(user=self)

    return self._token


# Add custom methods to User class
get_user_model().add_to_class('get_token', get_token)
