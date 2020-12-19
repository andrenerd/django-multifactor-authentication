# Multauth Example
# Email-Password-Authenticator:Passcode

The example shows how to add authentication, including rest endpoints, with the following settings:
- identifier: "email"
- secrets: "password", "passcode"

Such settings are pretty common for 2fa verification. User to be authenticated if and only if all of these parameters are passed and checked.


### Live

Live version of the example application is accesible (via web api) here: 
http://xxx.xxx


### Settings

```
AUTH_USER_MODEL = 'multauth.User'
AUTHENTICATION_BACKENDS = (
    'multauth.backends.ModelBackend',
)

MULTAUTH_SERVICES = [
  'multauth.services.EmailService',
  'multauth.services.AuthenticatorService',
]

MULTAUTH_FLOWS = (
    ('email', 'password', 'passcode'),
)
```