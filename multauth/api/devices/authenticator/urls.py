from django.urls import include, path

from .me import views as me_views
from .auth import views as auth_views


urlpatterns = [
    path('me/authenticator/key/', me_views.MeAuthenticatorKeyImageView.as_view(), name='me-authenticator-key'),
    path('me/authenticator/key/image', me_views.MeAuthenticatorKeyImageView.as_view(), name='me-authenticator-key-image'),
    path('me/authenticator/key/text', me_views.MeAuthenticatorKeyTextView.as_view(), name='me-authenticator-key-text'),
]

