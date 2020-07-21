from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class UserBackend(ModelBackend):

    def authenticate(self, request, **kwargs):
        # experimental
        for (identifier, secret) in UserModel._credentials:
            if identifier in kwargs and secret in kwargs:

                try:
                    identifier_args = {identifier: kwargs.get(identifier)}
                    user = UserModel._default_manager.get(**identifier_args)

                except UserModel.DoesNotExist:
                    # Run the default password hasher once to reduce the timing
                    # difference between an existing and a nonexistent user (#20760).
                    UserModel().set_password(password)

                else:
                    if self.user_can_authenticate(user):
                        if user.check_secrets(**kwargs):
                            return user
