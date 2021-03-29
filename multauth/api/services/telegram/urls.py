from django.urls import include, path

from .me import views as me_views
from .auth import views as auth_views

urlpatterns = [
    path('signup/verification/telegram/', auth_views.SignupVerificationTelegramView.as_view(), name='signup-verification-telegram'),
    path('signin/passcode/telegram/', auth_views.SigninPasscodeTelegramView.as_view(), name='signin-passcode-telegram'),
]

