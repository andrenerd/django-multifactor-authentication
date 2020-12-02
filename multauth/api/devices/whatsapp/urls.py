from django.urls import include, path

from .me import views as me_views
from .auth import views as auth_views


urlpatterns = [
    path('signup/verification/whatsapp/', auth_views.SignupVerificationWhatsappView.as_view(), name='signup-verification-whatsapp'),
    path('signin/passcode/whatsapp/', auth_views.SigninPasscodeWhatsappView.as_view(), name='signin-passcode-whatsapp'),
]

