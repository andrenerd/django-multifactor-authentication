from django.urls import include, path

from .me import views as me_views
from .auth import views as auth_views


urlpatterns = [
    path('me/passcode/', me_views.MePasscodeView.as_view(), name='me-passcode'),
    path('me/pushcode/', me_views.MePushcodeView.as_view(), name='me-pushcode'),
    path('signup/verification/phone/', auth_views.SignupVerificationPhoneView.as_view(), name='signup-verification-phone'),
]

