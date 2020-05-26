from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class UserBackend(ModelBackend):
    """
    Authenticates using multiple username fields (phone or email)
    """

    def authenticate(self, 
        request, username=None,
        phone=None, passcode=None,
        email=None, password=None,
        token=None, **kwargs
    ):

        # handle legacy scenarios
        if UserModel.USERNAME_FIELD == 'phone':
            phone = phone or username
        else:
            email = email or username

        # get user by identifier
        try:
            if phone:
                user = UserModel._default_manager.get(phone=phone)

            if email:
                user = UserModel._default_manager.get(email=email)

        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)

        # experimental
        # authenticate user by credentials
        else:
            if self.user_can_authenticate(user): # experimental
                # email or phone + password
                if password:
                    if user.check_password(password):
                        return user

                # phone + passcode + token
                if passcode:
                    if user.check_passcode(passcode):
                        if phone and user.verify_phone_token(token):
                            return user

                # email + token
                if token:
                    if email and user.verify_email_token(token):
                        return user
