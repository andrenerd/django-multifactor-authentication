# Multauth Example
# Email-Password-Phone:Passcode

The example shows how to add authentication, including rest endpoints, with the following settings:
- identifier: "email"
- secrets: "password", "passcode"

Such settings are pretty common for 2fa verification. User to be authenticated if and only if all of these parameters are passed and checked.

Some extra features that are handled out of the box and activated in the example:
- email: by default newly added or updated email addresses marked as non-confirmed and supposed to be  be verified
- passcode: to be sent on the phone via sms, by default phone is not confirmed and supposed to be verified before use for regular authentication.
