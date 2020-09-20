from django.urls import include, path

from .me import views as me_views
from .auth import views as auth_views


urlpatterns = [
    # path('me/phone/hardcode/', me_views.MeHardcodeView.as_view(), name='me-phone-hardcode'),
    path('me/phone/pushcode/', me_views.MePhonePushcodeView.as_view(), name='me-phone-pushcode'),
    path('signup/verification/phone/', auth_views.SignupVerificationPhoneView.as_view(), name='signup-verification-phone'),
    path('signin/passcode/phone/', auth_views.SigninPasscodePhoneView.as_view(), name='signin-passcode-phone'),
]

