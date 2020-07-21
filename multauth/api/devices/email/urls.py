from django.urls import include, path

from .me import views as me_views
from .auth import views as auth_views


urlpatterns = [
    path('me/password/', me_views.MePasswordView.as_view(), name='me-password'),
    path('signup/verification/email/', auth_views.SignupVerificationEmailView.as_view(), name='signup-verification-email'),
    path('signup/verification/email/<str:key>', auth_views.SignupVerificationEmailKeyView.as_view(), name='signup-verification-email-key'),
]
