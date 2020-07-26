# Django Multifactor Authentication


NB. Alpha version. Deep refactoring will be completed soon.


[![pypi version](https://img.shields.io/pypi/v/django-multifactor-authentication.svg)](https://pypi.org/project/django-multifactor-authentication/)


Flexible authentication for web, mobile, desktop and hybrid apps. It can be used for 1fa, 2fa and mfa cases. Easily configurable and extendable with new authentication methods or services. Authenticaton scenarios, called `flows`, based on the next `identifiers` and `secrets`, which can be used or not used in multiple combinations:
- username, email, phone, ...
- password, passcode (one-time pass or token), hardcode (device or card id), ...

and service providers:  
- Twilio
- SendGrid (to be specified)
- Nexmo (to be done)
- Amazon SNS (to be done)
- ...add yours




### Usage

The package creates custom user model, that could be used as is or as inherited. General priniciples for custom user models in Django are respected ([how it works](https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#substituting-a-custom-user-model)).


Base settings (required):
```
AUTH_USER_MODEL = 'multauth.User'
AUTHENTICATION_BACKENDS = (
    'multauth.backends.ModelBackend',
    # ...other backends
)

MULTAUTH_DEBUG = True # False by default
MULTAUTH_PASSCODE_LENGTH = 6 # size in digits
MULTAUTH_PASSCODE_EXPIRY = 3600 * 24 * 3 # time in seconds


MULTAUTH_FLOWS = (
  ('phone', 'hardcode', 'passcode',),
  ('email', 'password', 'passcode',),
  ('username', 'password',),
)

```


Extra settings (optional):  
(see built-in [devices](./multauth/devices), [providers](./multauth/providers) and [templates](./multauth/templates))  
```
MULTAUTH_DEVICES = [
  UsernameDevice,
  EmailDevice,
  PhoneDevice,
] # by default

MULTAUTH_DEVICE_EMAIL_PROVIDER = 'mail' # by default
MULTAUTH_DEVICE_PHONE_PROVIDER = 'twilio' # by default

MULTAUTH_DEVICE_EMAIL_TEMPLATE_NAME = 'custom'
MULTAUTH_DEVICE_EMAIL_VERIFICATION_VIEWNAME = 'custom'
MULTAUTH_DEVICE_PHONE_TEMPLATE_NAME = 'custom'
```


Provider specific settings (could be required):  
```
MULTAUTH_PROVIDER_TWILIO_ACCOUNT_SID = 'SID'
MULTAUTH_PROVIDER_TWILIO_AUTH_TOKEN = 'TOKEN'
MULTAUTH_PROVIDER_TWILIO_CALLER_ID = 'CALLER_ID'
```

