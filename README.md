# Django Multifactor Authentication


[![pypi version](https://img.shields.io/pypi/v/django-multifactor-authentication.svg)](https://pypi.org/project/django-multifactor-authentication/)


Flexible authentication for web, mobile, desktop and hybrid apps. It can be used for 1fa, 2fa and mfa cases. Easily configurable and extendable with new authentication methods or services. Authenticaton scenarios, called `flows`, are based on `identifiers` and `secrets`, which can be used or not used in multiple combinations:
- username, email, phone, ...
- password, passcode (one-time pass or token), hardcode (device or card id), ...

Full list of supported services and corresponding identifiers:
- Email
- Phone (as Sms)
- WhatsApp
- Google Authenticator
- Microsoft Authenticator
- Authy, andOTP, etc
- Yubikey (soon)
- ...add yours

and service providers:  
- Twilio
- Vonage (Nexmo)
- Amazon SNS (soon)
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
    # pattern: ('identifier', 'secret1', 'secret2', ...)
    ('phone', 'hardcode', 'passcode'),
    ('email', 'password', 'passcode'),
    ('username', 'password'),
    # ...etc
)

```
The flows mean that user could be authenticated with any of these sets of crendials, ie set of `identfier` and `secrets`. For example, this one: ('email', 'password', 'passcode',). Number of flows could be any, but in most cases only one or two are used.


Extra settings (optional):  
(see built-in [services](./multauth/services), [providers](./multauth/providers) and [templates](./multauth/templates))  
```
MULTAUTH_SERVICES = [
  'multauth.services.UsernameService',
  'multauth.services.EmailService',
  'multauth.services.PhoneService',
] # by default

MULTAUTH_DEBUG = True # False by default
MULTAUTH_PASSCODE_LENGTH = 6 # size in digits
MULTAUTH_PASSCODE_EXPIRY = 3600 # time in seconds
MULTAUTH_PASSCODE_SERVICE = 'multauth.services.PhoneService' # by default

MULTAUTH_SERVICE_EMAIL_PROVIDER = 'multauth.providers.MailProvider' # by default
MULTAUTH_SERVICE_PHONE_PROVIDER = 'multauth.providers.TwilioProvider' # by default

MULTAUTH_SERVICE_EMAIL_TEMPLATE_NAME = 'custom'
MULTAUTH_SERVICE_EMAIL_VERIFICATION_VIEWNAME = 'custom'
MULTAUTH_SERVICE_PHONE_TEMPLATE_NAME = 'custom'
```


Provider specific settings (could be required):  
```
MULTAUTH_PROVIDER_TWILIO_ACCOUNT_SID = 'SID'
MULTAUTH_PROVIDER_TWILIO_AUTH_TOKEN = 'TOKEN'
MULTAUTH_PROVIDER_TWILIO_CALLER_ID = 'CALLER_ID' # '+15005550006'

MULTAUTH_PROVIDER_VONAGE_API_KEY = 'KEY'
MULTAUTH_PROVIDER_VONAGE_API_SECRET = 'SECRET'
MULTAUTH_PROVIDER_VONAGE_BRAND_NAME = 'BRAND_NAME' # 'Vonage APIs'
```


### Usage more

Custom use cases and how to config or code them.


#### APIs

Package contains full set of [rest api endpoints](./multauth/api/urls.py), but it's optional. To activate it, `djangorestframework>=3.10.3` should be installed and the urls be included:
```
urlpatterns = [
    path(r'^', include('multauth.api.urls')),
]
```


#### User activation

Users are set as "active" on creation.
This behavior is not managed by settings for now (check for further updates).


#### Services verification

By default all services are set as "confirmed" on creation.
To change this behavior extra settings should be added, for example:  
```
MULTAUTH_SERVICE_EMAIL_CONFIRMED = False
MULTAUTH_SERVICE_PHONE_CONFIRMED = False
...
```

Non-comfirmed services will automatically be called for verification (token/key to be sent) on creation or idenfier updates. To invoke verification manually, call api endpoints:
- `multauth:signup-verification`

or model methods:
- `user.verify` for all non-confirmed services
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


