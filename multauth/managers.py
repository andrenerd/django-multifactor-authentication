from django.contrib.auth.models import UserManager as _UserManager


class UserManager(_UserManager):

    def _create_user(self, **fields):
        self.model.validate(**fields) # validate values
        user = self.model(**fields)

        user.clean() # normalize values
        user.set_secrets(**fields) # hash pass codes
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
