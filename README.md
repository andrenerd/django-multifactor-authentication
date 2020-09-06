# Django Multifactor Authentication


[![pypi version](https://img.shields.io/pypi/v/django-multifactorr-authentication.svg)](https://pypi.org/project/django-multifactor-authentication/)


Flexible authentication for web, mobile, desktop and hybrid apps. It can be used for 1fa, 2fa and mfa cases. Easily configurable and extendable with new authentication methods or services. Authenticaton scenarios, called `flows`, are based on `identifiers` and `secrets`, which can be used or not used in multiple combinations:
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
    # ...etc
)

MULTAUTH_FLOWS = (
    ('phone', 'hardcode', 'passcode',),
    ('email', 'password', 'passcode',),
    ('username', 'password',),
    # ...etc
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

MULTAUTH_DEBUG = True # False by default
MULTAUTH_PASSCODE_LENGTH = 6 # size in digits
MULTAUTH_PASSCODE_EXPIRY = 3600 # time in seconds

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



### Usage more

Custom use cases and how to config or code them.


#### User activation

Users are set as "active" on creation.
This behavior is not managed by settings for now (check for further updates).


#### Devices verification

By default all devices are set as "confirmed" on creation.
To change this behavior extra settings should be added, for example:  
```
MULTAUTH_DEVICE_EMAIL_CONFIRMED = False
MULTAUTH_DEVICE_PHONE_CONFIRMED = False
...
```

Non-comfirmed devices will automatically be called for verification (token/key to be sent) on creation or idenfier updates. To invoke verification manually, call api endpoints:
- `multauth:signup-verification`

or model methods:
- `user.verify` for all non-confirmed devices
- `user.verify_email` for email
- `user.verify_phone` for phone
- ...

And to complete verification process call api endpoints:
- `multauth:signup-verification-phone` to post the token
- `multauth:signup-verification-email` to post the token
- `multauth:signup-verification-email-key` as a classic in-email link to pass the key
- ...

or model methods:
- `user.verify_phone_token`
- `user.verify_email_token`
- `user.verify_email_key`
- ...


