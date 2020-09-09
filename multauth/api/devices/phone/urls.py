from django.urls import include, path

from .me import views as me_views
from .auth import views as auth_views


urlpatterns = [
    # path('me/phone/hardcode/', me_views.MeHardcodeView.as_view(), name='me-hardcode'),
    path('me/phone/pushcode/', me_views.MePhonePushcodeView.as_view(), name='me-pushcode'),
    path('signup/verification/phone/', auth_views.SignupVerificationPhoneView.as_view(), name='signup-verification-phone'),
]

