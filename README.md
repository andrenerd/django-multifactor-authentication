# Django Multiform Authentication


Combined web and mobile authentication for Django. It's not multi-factor, it's one-factor in multiple formats to build multi-purpose backends for web and mobile apps. Supported credential pairs:
- email/password
- phone/passcode
- ...maybe more later


### USAGE

The package creates custom user model, that could be used as is or as inherited. General priniciples for custom user models in Django are respected ([how it works](https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#substituting-a-custom-user-model))

Basic settings:
```
AUTH_USER_MODEL = 'multauth.User'

MULTAUTH_DEBUG = True # False by default
MULTAUTH_TOKEN_LENGTH = 6 # size in digits
MULTAUTH_TOKEN_EXPIRY = 3600 * 24 * 3 # time in seconds

MULTAUTH_PROVIDER_TWILIO_ACCOUNT_SID = 'SID'
MULTAUTH_PROVIDER_TWILIO_AUTH_TOKEN = 'TOKEN'
MULTAUTH_PROVIDER_TWILIO_CALLER_ID = 'CALLER_ID'
```
