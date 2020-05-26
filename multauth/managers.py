from django.contrib.auth.models import UserManager


class UserManager(UserManager):

    def _create_user(self,
        phone=None, passcode=None,
        email=None, password=None,
        **extra_fields
    ):
        if not phone and not email:
            raise ValueError('At least one of the identifiers (phone, email) must be set')

        if email:
            email = self.normalize_email(email)

        user = self.model(phone=phone, email=email, **extra_fields)
        user.create_username()

        if passcode:
            user.set_passcode(passcode)

        if password:
            user.set_password(password)

        user.save(using=self._db)

        return user

    def create_user(self, phone=None, passcode=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(phone, passcode, email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(None, email, password, **extra_fields)
