from django.urls import include, path

from .me import views as me_views
from .auth import views as auth_views
from .services import urls as services_urls


app_name = 'multauth'

urlpatterns = [
    path('me/', me_views.MeView.as_view(), name='me'),
    path('me/password/', me_views.MePasswordView.as_view(), name='me-password'),
    path('me/passcode/', me_views.MePasscodeView.as_view(), name='me-passcode'),
    path('signin/', auth_views.SigninView.as_view(), name='signin'),
    path('signup/', auth_views.SignupView.as_view(), name='signup'),
    path('signup/verification/', auth_views.SignupVerificationView.as_view(), name='signup-verification'),

    path(r'^', include(services_urls)),
]
