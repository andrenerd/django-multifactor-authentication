# Django Multiform Authentication

NB. Complete refactoring coming soon.

Combined web and mobile authentication for Django. It's not multi-factor, it's one-factor in multiple formats. Easily configurable and extendable with new authentication methods or services. Supported out-of-the-box methods by credential pairs:  
- email / password
- phone / passcode
- ...add yours

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
    'multauth.backends.UserBackend',
    # ...other custom backends
)

MULTAUTH_DEBUG = True # False by default
MULTAUTH_TOKEN_LENGTH = 6 # size in digits
MULTAUTH_TOKEN_EXPIRY = 3600 * 24 * 3 # time in seconds
```


Extra settings (optional):  
(see built-in [devices](/), [providers](/) and [templates](/))  
```
MULTAUTH_DEVICES = [
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




### Flows


##### Email
This authentication flow is pretty the same as provided by Django by default. Extra feature
is that it's handaled by rest api too, not function calls only.
- User provides `email` as identifier (email address), [url]
- User confirms the identifier (`email`) [url, func]
- Able to signin using the credentials: `email`/`password`
- ...add more


##### Phone
- User provides `phone` as identifier (phone number), [url]
- User confirms the identifier (`phone`) [url, func]
- Able to signin using the credentials: `phone`/`secret`*** [url]
- ...add more

*** `passcode` (set by user explicitly) or `token` (set by app automatically) supposed to be used as secret


##### More
Let us know what other authentication flows would be nice to add.
For example, you decide to add `microchip implants` based authentication. There are several simple steps to take:
- to add Device (as example)[link?]
- to add at least one Provider associated with the Device (as example)[link?]
- to extend User model fields and methods (as example)[link?], [as example, _EmailAbstractUser]
- to extend api with new endpoints [see]
- tweak settings to activate the flow:
```
MULTAUTH_DEVICES = [
  PhoneDevice,
  ChipDevice, # long-awaited microchip implants ;)
]

AUTH_USER_MODEL = 'app.ChipPhoneUser'
```


