from django.contrib.auth.models import UserManager as _UserManager
from django.contrib.auth.hashers import check_password, make_password


class UserManager(_UserManager):

    def _create_user(self, username=None, password=None, **fields):
        identifiers = self.model.IDENTIFIERS
        identifiers_in_fields = [x for x in identifiers if x in fields.keys()]

        if not username and not identifiers_in_fields:
            raise ValueError('The given username or any identifier must be set')

        user = self.model(**fields)
        user.clean() # normalize values

        if username:
            user.username = username

        if password:
            user.password = make_password(password)

        user.save(using=self._db)
        return user

    def create_user(self, **fields):
        if hasattr(self.model, 'is_staff'):
            fields.setdefault('is_staff', False)

        if hasattr(self.model, 'is_superuser'):
            fields.setdefault('is_superuser', False)

        return self._create_user(**fields)

    def create_superuser(self, **fields):
        if hasattr(self.model, 'is_staff'):
            fields.setdefault('is_staff', True)
            if fields.get('is_staff') is not True:
                raise ValueError('Superuser must have is_staff=True.')

        if hasattr(self.model, 'is_superuser'):
            fields.setdefault('is_superuser', True)
            if fields.get('is_superuser') is not True:
                raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(**fields)
